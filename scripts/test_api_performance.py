#!/usr/bin/env python3
"""
Quick API test to get performance metrics for the paper.
"""

import requests
import time
import json
import sys
sys.path.append('.')

from src.models import EdgeOptimizedModel
from src.features import FeatureExtractor
from pathlib import Path

def test_direct_model_performance():
    """Test model performance directly (without API server)."""
    print("🔬 Testing Direct Model Performance...")
    print("=" * 50)
    
    # Load model
    models_dir = Path("models")
    edge_model = EdgeOptimizedModel(models_dir)
    edge_model.load_models()
    
    # Initialize feature extractor
    feature_extractor = FeatureExtractor()
    
    # Test URLs
    test_urls = [
        "https://google.com",
        "http://malicious-site.tk/login.php?redirect=evil", 
        "https://github.com/microsoft/vscode",
        "http://192.168.1.1/admin.php",
        "https://shortened.ly/abc123",
        "http://www.bank-security-update.com/verify.php",
        "https://facebook.com/profile",
        "http://suspicious-domain.ml/download.exe"
    ]
    
    results = []
    total_start = time.time()
    
    for i, url in enumerate(test_urls):
        start_time = time.time()
        
        # Create mock row for feature extraction
        mock_row = {
            'url': url,
            'Domain': url.split('/')[2] if '://' in url else url,
            'label': 0,
            'source': 'test',
            'TTL': 3600,
            'Name_Server_Count': 2,
            'Domain_Age': 365,
            'Page_Rank': -1,
            'Alexa_Rank': -1,
            'Organization': None,
            'Registrant_Name': None,
            'shortened': 0,
            'puny_coded': 0,
            'obfuscate_at_sign': 0
        }
        
        # Extract features
        features = {}
        lexical_features = feature_extractor.url_extractor.extract_features(url)
        features.update(lexical_features)
        metadata_features = feature_extractor.domain_extractor.extract_features(mock_row)
        features.update(metadata_features)
        
        # Predict
        result = edge_model.predict_single(features)
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        results.append({
            'url': url,
            'prediction': result['label'],
            'confidence': result['confidence'],
            'processing_time_ms': processing_time
        })
        
        print(f"{i+1}. {url}")
        print(f"   → {result['label']} (confidence: {result['confidence']:.3f})")
        print(f"   → Processing time: {processing_time:.2f}ms")
        print()
    
    total_time = (time.time() - total_start) * 1000
    avg_time = total_time / len(test_urls)
    
    print(f"📊 Performance Summary:")
    print(f"   Total processing time: {total_time:.2f}ms")
    print(f"   Average per URL: {avg_time:.2f}ms")
    print(f"   Throughput: {1000/avg_time:.2f} URLs/sec")
    
    # Calculate statistics
    processing_times = [r['processing_time_ms'] for r in results]
    
    performance_stats = {
        'mean_latency_ms': sum(processing_times) / len(processing_times),
        'min_latency_ms': min(processing_times),
        'max_latency_ms': max(processing_times),
        'total_urls_tested': len(test_urls),
        'throughput_urls_per_sec': 1000 / (sum(processing_times) / len(processing_times)),
        'total_processing_time_ms': total_time
    }
    
    return performance_stats, results

def main():
    """Main test function."""
    print("🚀 Edge-AI URL Detection - Performance Testing")
    print("=" * 60)
    
    # Test direct model performance
    stats, detailed_results = test_direct_model_performance()
    
    # Save results
    results_summary = {
        'performance_statistics': stats,
        'detailed_results': detailed_results,
        'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to file
    with open('reports/api_performance_test.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\n✅ Performance test completed!")
    print(f"📁 Results saved to reports/api_performance_test.json")
    
    # Create summary report
    with open('reports/api_performance_summary.txt', 'w') as f:
        f.write("Edge-AI URL Detection - API Performance Test\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Performance Statistics:\n")
        f.write(f"  Mean Latency: {stats['mean_latency_ms']:.2f} ms\n")
        f.write(f"  Min Latency: {stats['min_latency_ms']:.2f} ms\n")
        f.write(f"  Max Latency: {stats['max_latency_ms']:.2f} ms\n")
        f.write(f"  Throughput: {stats['throughput_urls_per_sec']:.2f} URLs/sec\n")
        f.write(f"  Total URLs Tested: {stats['total_urls_tested']}\n\n")
        
        f.write("Individual Test Results:\n")
        f.write("-" * 30 + "\n")
        for result in detailed_results:
            f.write(f"URL: {result['url']}\n")
            f.write(f"  Prediction: {result['prediction']}\n")
            f.write(f"  Confidence: {result['confidence']:.3f}\n")
            f.write(f"  Processing Time: {result['processing_time_ms']:.2f}ms\n\n")
    
    print(f"📁 Summary saved to reports/api_performance_summary.txt")

if __name__ == "__main__":
    main()