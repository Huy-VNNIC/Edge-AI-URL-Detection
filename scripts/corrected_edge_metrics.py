#!/usr/bin/env python3
"""
Fixed Edge Metrics Evaluation
Provides accurate model memory usage and API performance measurements
Corrects the issues from previous evaluation where system RAM was reported instead of model overhead
"""

import os
import sys
import time
import psutil
import requests
import pandas as pd
import numpy as np
from pathlib import Path
import gc
import json
import logging

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

import pickle
from sklearn.ensemble import RandomForestClassifier

# Add project root to path
sys.path.append('.')
from src.features import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def measure_model_memory_footprint():
    """Measure actual model memory footprint (not system RAM)"""
    logger.info("Measuring model memory footprint...")
    
    # Load training data
    train_file = "data/processed/train_features.csv"
    if not os.path.exists(train_file):
        logger.error(f"Training features not found at {train_file}")
        return None
    
    # Measure baseline memory
    process = psutil.Process()
    baseline_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Load data (sample to avoid memory issues)
    train_df = pd.read_csv(train_file, nrows=10000)  # Sample for memory measurement
    feature_cols = [col for col in train_df.columns if col not in ['url', 'domain', 'label', 'source']]
    X = train_df[feature_cols].fillna(-1)
    y = train_df['label']
    
    # Memory after data loading
    data_memory = process.memory_info().rss / (1024 * 1024)
    data_overhead = data_memory - baseline_memory
    
    # Train model
    logger.info("Training Random Forest model...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=1  # Use single thread for consistent memory measurement
    )
    
    rf.fit(X, y)
    
    # Memory after model training
    model_memory = process.memory_info().rss / (1024 * 1024)
    model_overhead = model_memory - data_memory
    
    # Serialize model to measure file size
    model_path = "models/temp_model_for_size.pkl"
    os.makedirs("models", exist_ok=True)
    
    with open(model_path, 'wb') as f:
        pickle.dump(rf, f)
    
    model_file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
    os.remove(model_path)  # Clean up
    
    # Measure prediction memory
    extractor = FeatureExtractor()
    prediction_memory_before = process.memory_info().rss / (1024 * 1024)
    
    # Extract features and predict for sample URLs
    sample_urls = ["https://example.com/test", "http://malicious.site/evil.exe"]
    for url in sample_urls:
        sample_df = pd.DataFrame({'url': [url], 'label': [0]})
        features_df = extractor.extract_all_features(sample_df)
        X_sample = features_df[feature_cols].fillna(-1)
        _ = rf.predict_proba(X_sample)
    
    prediction_memory_after = process.memory_info().rss / (1024 * 1024)
    prediction_overhead = prediction_memory_after - prediction_memory_before
    
    memory_metrics = {
        'baseline_memory_mb': baseline_memory,
        'data_loading_overhead_mb': data_overhead,
        'model_training_overhead_mb': model_overhead,
        'model_file_size_mb': model_file_size,
        'prediction_overhead_mb': max(0, prediction_overhead),  # Ensure non-negative
        'total_model_footprint_mb': model_overhead + max(0, prediction_overhead),
        'trained_model': rf,
        'feature_extractor': extractor
    }
    
    return memory_metrics

def measure_prediction_latency(model, extractor, num_samples=500):
    """Measure prediction latency with proper statistical analysis"""
    logger.info(f"Measuring prediction latency with {num_samples} samples...")
    
    test_urls = [
        "https://example.com/path/to/resource",
        "http://malicious-domain.ru/exploit.exe",
        "https://legitimate-site.org/services/api/v1/data",
        "http://192.168.1.1:8080/admin/login",
        "https://shortened.ly/abc123"
    ]
    
    # Extend to num_samples
    extended_urls = (test_urls * (num_samples // len(test_urls) + 1))[:num_samples]
    
    latencies = []
    feature_extraction_times = []
    model_prediction_times = []
    
    # Get feature columns
    train_df = pd.read_csv("data/processed/train_features.csv", nrows=1)
    feature_cols = [col for col in train_df.columns if col not in ['url', 'domain', 'label', 'source']]
    
    for i, url in enumerate(extended_urls):
        if i % 100 == 0:
            logger.info(f"Processing URL {i+1}/{num_samples}")
        
        # Measure total latency
        start_time = time.perf_counter()
        
        # Feature extraction
        feature_start = time.perf_counter()
        sample_df = pd.DataFrame({'url': [url], 'label': [0]})
        features_df = extractor.extract_all_features(sample_df)
        X_sample = features_df[feature_cols].fillna(-1)
        feature_end = time.perf_counter()
        
        # Model prediction
        pred_start = time.perf_counter()
        prediction = model.predict_proba(X_sample)[0]
        pred_end = time.perf_counter()
        
        end_time = time.perf_counter()
        
        # Record timings
        total_latency = (end_time - start_time) * 1000  # ms
        feature_time = (feature_end - feature_start) * 1000  # ms
        pred_time = (pred_end - pred_start) * 1000  # ms
        
        latencies.append(total_latency)
        feature_extraction_times.append(feature_time)
        model_prediction_times.append(pred_time)
    
    # Calculate statistics
    latency_stats = {
        'mean_latency_ms': np.mean(latencies),
        'median_latency_ms': np.median(latencies),
        'p95_latency_ms': np.percentile(latencies, 95),
        'p99_latency_ms': np.percentile(latencies, 99),
        'std_latency_ms': np.std(latencies),
        'throughput_urls_per_sec': 1000 / np.mean(latencies),
        'feature_extraction_mean_ms': np.mean(feature_extraction_times),
        'model_prediction_mean_ms': np.mean(model_prediction_times),
        'feature_extraction_percentage': np.mean(feature_extraction_times) / np.mean(latencies) * 100,
        'model_prediction_percentage': np.mean(model_prediction_times) / np.mean(latencies) * 100
    }
    
    return latency_stats

def test_api_performance():
    """Test API performance if it's running"""
    logger.info("Testing API performance...")
    
    api_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        health_response = requests.get(f"{api_url}/health", timeout=5)
        if health_response.status_code != 200:
            logger.warning("API health check failed")
            return None
    except requests.exceptions.RequestException:
        logger.warning("API not running")
        return None
    
    # Test URLs
    test_urls = [
        "https://example.com/safe",
        "http://malicious.site/evil.exe",
        "https://legitimate-business.com/contact"
    ]
    
    api_latencies = []
    success_count = 0
    
    for i in range(50):  # Test with 50 requests
        url = test_urls[i % len(test_urls)]
        
        try:
            start_time = time.perf_counter()
            response = requests.post(
                f"{api_url}/detect",
                json={"url": url},
                timeout=10
            )
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                success_count += 1
                latency = (end_time - start_time) * 1000  # ms
                api_latencies.append(latency)
            
        except requests.exceptions.RequestException:
            pass
    
    if api_latencies:
        api_stats = {
            'mean_api_latency_ms': np.mean(api_latencies),
            'p95_api_latency_ms': np.percentile(api_latencies, 95),
            'api_success_rate': success_count / 50,
            'api_throughput_req_per_sec': 1000 / np.mean(api_latencies)
        }
    else:
        api_stats = {
            'mean_api_latency_ms': 0,
            'p95_api_latency_ms': 0,
            'api_success_rate': 0,
            'api_throughput_req_per_sec': 0
        }
    
    return api_stats

def main():
    """Main edge metrics evaluation pipeline"""
    logger.info("Starting corrected edge metrics evaluation...")
    
    # Create output directory
    os.makedirs("reports/edge_metrics", exist_ok=True)
    
    # 1. Measure model memory footprint
    memory_metrics = measure_model_memory_footprint()
    if not memory_metrics:
        logger.error("Failed to measure memory metrics")
        return
    
    logger.info("Memory metrics completed")
    
    # 2. Measure prediction latency
    latency_metrics = measure_prediction_latency(
        memory_metrics['trained_model'], 
        memory_metrics['feature_extractor']
    )
    
    logger.info("Latency metrics completed")
    
    # 3. Test API performance
    api_metrics = test_api_performance()
    
    # 4. Combine all metrics
    edge_metrics = {
        'memory': memory_metrics,
        'latency': latency_metrics,
        'api': api_metrics,
        'edge_compliance': {
            'model_size_under_1mb': memory_metrics['model_file_size_mb'] < 1.0,
            'latency_under_200ms': latency_metrics['p95_latency_ms'] < 200,
            'memory_footprint_mb': memory_metrics['total_model_footprint_mb'],
            'edge_ready': (memory_metrics['model_file_size_mb'] < 1.0 and 
                          latency_metrics['p95_latency_ms'] < 200)
        }
    }
    
    # Remove non-serializable objects for JSON export
    export_metrics = edge_metrics.copy()
    del export_metrics['memory']['trained_model']
    del export_metrics['memory']['feature_extractor']
    
    # Save detailed results
    with open("reports/edge_metrics/corrected_edge_metrics.json", "w") as f:
        json.dump(export_metrics, f, indent=2, default=convert_numpy_types)
    
    # Generate report
    generate_edge_report(edge_metrics)
    
    logger.info("Corrected edge metrics evaluation completed!")

def generate_edge_report(metrics):
    """Generate comprehensive edge metrics report"""
    
    print("\n" + "="*70)
    print("            CORRECTED EDGE-AI METRICS REPORT")
    print("="*70)
    
    # Memory Analysis
    memory = metrics['memory']
    print(f"\n1. MEMORY FOOTPRINT ANALYSIS")
    print("-" * 35)
    print(f"Model File Size: {memory['model_file_size_mb']:.2f} MB")
    print(f"Training Overhead: {memory['model_training_overhead_mb']:.2f} MB")
    print(f"Prediction Overhead: {memory['prediction_overhead_mb']:.2f} MB")
    print(f"Total Model Footprint: {memory['total_model_footprint_mb']:.2f} MB")
    
    # Latency Analysis
    latency = metrics['latency']
    print(f"\n2. PREDICTION LATENCY ANALYSIS")
    print("-" * 40)
    print(f"Mean Latency: {latency['mean_latency_ms']:.2f} ms")
    print(f"P95 Latency: {latency['p95_latency_ms']:.2f} ms")
    print(f"Throughput: {latency['throughput_urls_per_sec']:.1f} URLs/sec")
    print(f"\nLatency Breakdown:")
    print(f"  Feature Extraction: {latency['feature_extraction_mean_ms']:.2f} ms ({latency['feature_extraction_percentage']:.1f}%)")
    print(f"  Model Prediction: {latency['model_prediction_mean_ms']:.2f} ms ({latency['model_prediction_percentage']:.1f}%)")
    
    # API Performance
    if metrics['api']:
        api = metrics['api']
        print(f"\n3. API PERFORMANCE")
        print("-" * 25)
        print(f"Mean API Latency: {api['mean_api_latency_ms']:.2f} ms")
        print(f"Success Rate: {api['api_success_rate']*100:.1f}%")
        print(f"API Throughput: {api['api_throughput_req_per_sec']:.1f} req/sec")
    else:
        print(f"\n3. API PERFORMANCE")
        print("-" * 25)
        print("API not running - metrics unavailable")
    
    # Edge Compliance
    compliance = metrics['edge_compliance']
    print(f"\n4. EDGE DEPLOYMENT COMPLIANCE")
    print("-" * 40)
    print(f"Model Size < 1MB: {'✅ PASS' if compliance['model_size_under_1mb'] else '❌ FAIL'} ({memory['model_file_size_mb']:.2f} MB)")
    print(f"Latency < 200ms: {'✅ PASS' if compliance['latency_under_200ms'] else '❌ FAIL'} ({latency['p95_latency_ms']:.1f}ms P95)")
    print(f"Edge Ready: {'✅ YES' if compliance['edge_ready'] else '❌ NO'}")
    
    # Save formatted report
    with open("reports/edge_metrics/corrected_edge_summary.txt", "w") as f:
        f.write("CORRECTED EDGE-AI METRICS SUMMARY\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Model File Size: {memory['model_file_size_mb']:.2f} MB\n")
        f.write(f"Total Memory Footprint: {memory['total_model_footprint_mb']:.2f} MB\n")
        f.write(f"Mean Prediction Latency: {latency['mean_latency_ms']:.2f} ms\n")
        f.write(f"P95 Latency: {latency['p95_latency_ms']:.2f} ms\n")
        f.write(f"Throughput: {latency['throughput_urls_per_sec']:.1f} URLs/sec\n")
        f.write(f"Edge Deployment Ready: {'YES' if compliance['edge_ready'] else 'NO'}\n")

if __name__ == "__main__":
    main()