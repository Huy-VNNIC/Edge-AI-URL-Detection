#!/usr/bin/env python3
"""
Real API Performance Benchmark
Tests the actual FastAPI server under realistic deployment conditions
Measures end-to-end latency including HTTP overhead
"""

import requests
import time
import json
import asyncio
import concurrent.futures
from statistics import mean, median
from typing import List, Dict
import sys
from pathlib import Path

def test_api_server(base_url: str = "http://localhost:8000", num_requests: int = 100) -> Dict:
    """Test API server performance with real HTTP requests"""
    
    # Test URLs (mix of benign and suspicious patterns)
    test_urls = [
        "https://google.com",
        "https://github.com/microsoft/vscode", 
        "https://stackoverflow.com/questions/python",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://docs.python.org/3/library/json.html",
        "http://malicious-site.tk/login.php?redirect=evil",
        "http://192.168.1.1/admin.php",
        "http://suspicious-domain.ml/download.exe",
        "https://shortened.ly/abc123",
        "http://www.bank-security-update.com/verify.php"
    ]
    
    print(f"🚀 Testing API at {base_url}")
    print(f"📊 Running {num_requests} requests...")
    
    # Check if API is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            return {"error": "API health check failed", "status_code": health_response.status_code}
    except Exception as e:
        return {"error": f"Cannot connect to API: {e}"}
    
    latencies = []
    successes = 0
    errors = 0
    
    for i in range(num_requests):
        url = test_urls[i % len(test_urls)]
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/detect",
                json={"url": url, "include_metadata": False},
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            if response.status_code == 200:
                successes += 1
                # Validate response format
                result = response.json()
                required_fields = ['prediction', 'probability', 'label', 'confidence']
                if not all(field in result for field in required_fields):
                    print(f"⚠️ Invalid response format: {result}")
            else:
                errors += 1
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            errors += 1
            latencies.append(10000)  # 10s timeout penalty
            print(f"❌ Request failed: {e}")
        
        if (i + 1) % 20 == 0:
            print(f"   Progress: {i+1}/{num_requests} requests ({successes} successful)")
    
    # Calculate statistics
    if latencies:
        latencies.sort()
        p95_idx = int(0.95 * len(latencies))
        p99_idx = int(0.99 * len(latencies))
        
        stats = {
            "total_requests": num_requests,
            "successful_requests": successes,
            "failed_requests": errors,
            "success_rate": successes / num_requests,
            "mean_latency_ms": mean(latencies),
            "median_latency_ms": median(latencies),
            "p95_latency_ms": latencies[p95_idx] if p95_idx < len(latencies) else latencies[-1],
            "p99_latency_ms": latencies[p99_idx] if p99_idx < len(latencies) else latencies[-1],
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "throughput_req_per_sec": successes / (sum(latencies) / 1000) if latencies else 0
        }
    else:
        stats = {
            "total_requests": num_requests,
            "successful_requests": 0,
            "failed_requests": num_requests,
            "success_rate": 0.0,
            "mean_latency_ms": 0.0,
            "median_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "p99_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "throughput_req_per_sec": 0.0
        }
    
    return stats

def test_concurrent_load(base_url: str = "http://localhost:8000", 
                        concurrent_users: int = 10, 
                        requests_per_user: int = 10) -> Dict:
    """Test API under concurrent load"""
    
    print(f"🔥 Load testing: {concurrent_users} concurrent users, {requests_per_user} req each")
    
    test_urls = [
        "https://google.com",
        "http://malicious-site.tk/login.php",
        "https://github.com/repos",
        "http://suspicious.ml/download"
    ]
    
    def user_session(user_id: int) -> List[float]:
        """Simulate a user session with multiple requests"""
        user_latencies = []
        
        for req_num in range(requests_per_user):
            url = test_urls[(user_id + req_num) % len(test_urls)]
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{base_url}/detect",
                    json={"url": url},
                    timeout=5
                )
                end_time = time.time()
                
                latency_ms = (end_time - start_time) * 1000
                user_latencies.append(latency_ms)
                
            except Exception:
                user_latencies.append(5000)  # 5s penalty for failures
        
        return user_latencies
    
    # Run concurrent sessions
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(user_session, user_id) for user_id in range(concurrent_users)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    end_time = time.time()
    
    # Aggregate results
    all_latencies = [latency for user_latencies in results for latency in user_latencies]
    total_requests = len(all_latencies)
    total_time = end_time - start_time
    
    load_stats = {
        "concurrent_users": concurrent_users,
        "requests_per_user": requests_per_user,
        "total_requests": total_requests,
        "total_time_seconds": total_time,
        "overall_throughput": total_requests / total_time,
        "mean_latency_ms": mean(all_latencies),
        "p95_latency_ms": sorted(all_latencies)[int(0.95 * len(all_latencies))],
        "successful_rate": len([l for l in all_latencies if l < 5000]) / total_requests
    }
    
    return load_stats

def main():
    """Main benchmark function"""
    
    print("🎯 Edge-AI API Performance Benchmark")
    print("=" * 50)
    
    # Sequential performance test
    sequential_stats = test_api_server(num_requests=100)
    
    print("\n📊 SEQUENTIAL TEST RESULTS:")
    print("-" * 30)
    for key, value in sequential_stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # Load test (if sequential test passed)
    if sequential_stats.get("success_rate", 0) > 0.5:
        print("\n🔥 Running load test...")
        load_stats = test_concurrent_load(concurrent_users=5, requests_per_user=10)
        
        print("\n📊 LOAD TEST RESULTS:")
        print("-" * 30)
        for key, value in load_stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    else:
        load_stats = {"error": "Sequential test failed, skipping load test"}
    
    # Save results
    results = {
        "sequential_performance": sequential_stats,
        "load_performance": load_stats,
        "test_timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to reports
    output_file = Path("reports/api_benchmark_results.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Generate summary report
    print("\n" + "="*60)
    print("🎯 FINAL API PERFORMANCE SUMMARY")
    print("="*60)
    
    if sequential_stats.get("success_rate", 0) > 0:
        print(f"✅ Mean API Latency: {sequential_stats['mean_latency_ms']:.2f} ms")
        print(f"✅ P95 API Latency: {sequential_stats['p95_latency_ms']:.2f} ms") 
        print(f"✅ Success Rate: {sequential_stats['success_rate']*100:.1f}%")
        print(f"✅ API Throughput: {sequential_stats['throughput_req_per_sec']:.1f} req/sec")
        print(f"✅ Edge Compliant: {'YES' if sequential_stats['p95_latency_ms'] < 200 else 'NO'}")
    else:
        print("❌ API Performance Test FAILED")
        print("   - Check if API server is running")
        print("   - Verify endpoint URLs")
        print("   - Check model loading")

if __name__ == "__main__":
    main()