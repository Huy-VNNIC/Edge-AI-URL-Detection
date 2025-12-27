#!/usr/bin/env python3
"""
Complete evaluation pipeline for Edge-AI malicious URL detection system.
Tests accuracy, latency, memory usage, and edge deployment performance.
"""

import pandas as pd
import numpy as np
import time
import psutil
import requests
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
import sys
sys.path.append('.')

from src.models import EdgeOptimizedModel
from src.features import URLLexicalFeatures
from src.utils import load_config, setup_logging, ensure_dir

logger = setup_logging()

class PerformanceEvaluator:
    """Comprehensive performance evaluation for edge deployment."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.results = {}
        
    def evaluate_model_accuracy(self, model_path: Path, test_data_path: Path) -> Dict:
        """Evaluate model accuracy on test dataset."""
        logger.info("Evaluating model accuracy...")
        
        # Load test data
        df_test = pd.read_csv(test_data_path)
        
        feature_cols = [col for col in df_test.columns if col not in ['label', 'source']]
        X_test = df_test[feature_cols].values
        y_test = df_test['label'].values
        
        # Handle NaN values
        X_test = np.nan_to_num(X_test, 0)
        
        # Load model
        config = load_config()
        edge_model = EdgeOptimizedModel(model_path)
        edge_model.load_models()
        
        # Make predictions
        predictions, probabilities = edge_model.rf_model.predict(X_test)
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        roc_auc = roc_auc_score(y_test, probabilities)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'test_samples': len(y_test),
            'true_positives': ((predictions == 1) & (y_test == 1)).sum(),
            'true_negatives': ((predictions == 0) & (y_test == 0)).sum(),
            'false_positives': ((predictions == 1) & (y_test == 0)).sum(),
            'false_negatives': ((predictions == 0) & (y_test == 1)).sum()
        }
        
    def evaluate_inference_latency(self, model_path: Path, num_samples: int = 1000) -> Dict:
        """Evaluate inference latency on various input sizes."""
        logger.info(f"Evaluating inference latency with {num_samples} samples...")
        
        # Load model and feature extractor
        config = load_config()
        edge_model = EdgeOptimizedModel(model_path)
        edge_model.load_models()
        
        from src.features import FeatureExtractor
        feature_extractor = FeatureExtractor()
        
        # Test URLs
        test_urls = [
            "http://example.com",
            "https://google.com/search?q=test",
            "http://malicious-site.tk/login.php?redirect=evil",
            "https://legitimate-bank.com/secure/login",
            "http://192.168.1.1/admin",
            "https://shortened.ly/abc123",
            "http://very-long-suspicious-domain-name-with-lots-of-hyphens.ml/path/to/file.exe"
        ]
        
        # Single inference latency
        single_latencies = []
        for i in range(num_samples):
            url = np.random.choice(test_urls)
            start_time = time.time()
            
            # Create a mock row for full feature extraction
            mock_row = pd.Series({
                'url': url,
                'Domain': url,
                'label': 0,
                'source': 'test'
            })
            
            # Extract full features like in training
            features = {}
            lexical_features = feature_extractor.url_extractor.extract_features(url)
            features.update(lexical_features)
            metadata_features = feature_extractor.domain_extractor.extract_features(mock_row)
            features.update(metadata_features)
            
            result = edge_model.predict_single(features)
            
            latency = (time.time() - start_time) * 1000  # ms
            single_latencies.append(latency)
            
        # Batch inference latency
        batch_sizes = [1, 10, 50, 100]
        batch_results = {}
        
        for batch_size in batch_sizes:
            batch_urls = np.random.choice(test_urls, batch_size).tolist()
            
            start_time = time.time()
            
            # Extract features for batch
            batch_features = []
            for url in batch_urls:
                mock_row = pd.Series({
                    'url': url,
                    'Domain': url,
                    'label': 0,
                    'source': 'test'
                })
                
                features = {}
                lexical_features = feature_extractor.url_extractor.extract_features(url)
                features.update(lexical_features)
                metadata_features = feature_extractor.domain_extractor.extract_features(mock_row)
                features.update(metadata_features)
                
                # Convert to ordered feature array
                feature_values = []
                for feature_name in edge_model.rf_model.feature_names:
                    feature_values.append(features.get(feature_name, 0.0))
                batch_features.append(feature_values)
                
            # Predict batch
            batch_array = np.array(batch_features)
            results = edge_model.predict_batch(batch_array)
            
            batch_latency = (time.time() - start_time) * 1000  # ms
            per_sample_latency = batch_latency / batch_size
            
            batch_results[batch_size] = {
                'total_latency_ms': batch_latency,
                'per_sample_latency_ms': per_sample_latency,
                'throughput_samples_per_sec': 1000 / per_sample_latency
            }
            
        return {
            'single_inference': {
                'mean_latency_ms': np.mean(single_latencies),
                'median_latency_ms': np.median(single_latencies),
                'p95_latency_ms': np.percentile(single_latencies, 95),
                'p99_latency_ms': np.percentile(single_latencies, 99),
                'min_latency_ms': np.min(single_latencies),
                'max_latency_ms': np.max(single_latencies)
            },
            'batch_inference': batch_results
        }
        
    def evaluate_memory_usage(self, model_path: Path) -> Dict:
        """Evaluate memory usage during model loading and inference."""
        logger.info("Evaluating memory usage...")
        
        # Baseline memory
        baseline_memory = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # Load model and measure memory
        config = load_config()
        edge_model = EdgeOptimizedModel(model_path)
        
        before_load = psutil.virtual_memory().used / 1024 / 1024
        edge_model.load_models()
        after_load = psutil.virtual_memory().used / 1024 / 1024
        
        model_memory = after_load - before_load
        
        # Measure memory during inference
        from src.features import FeatureExtractor
        feature_extractor = FeatureExtractor()
        
        inference_memories = []
        for _ in range(100):
            before_inference = psutil.virtual_memory().used / 1024 / 1024
            
            mock_row = pd.Series({
                'url': "http://example.com/test",
                'Domain': "example.com",
                'label': 0,
                'source': 'test'
            })
            
            features = {}
            lexical_features = feature_extractor.url_extractor.extract_features("http://example.com/test")
            features.update(lexical_features)
            metadata_features = feature_extractor.domain_extractor.extract_features(mock_row)
            features.update(metadata_features)
            
            result = edge_model.predict_single(features)
            
            after_inference = psutil.virtual_memory().used / 1024 / 1024
            inference_memory = after_inference - before_inference
            
            inference_memories.append(inference_memory)
            
        return {
            'baseline_memory_mb': baseline_memory,
            'model_loading_memory_mb': model_memory,
            'total_memory_after_load_mb': after_load,
            'inference_memory_overhead_mb': {
                'mean': np.mean(inference_memories),
                'max': np.max(inference_memories),
                'min': np.min(inference_memories)
            }
        }
        
    def evaluate_api_performance(self, api_url: str = "http://localhost:8000", 
                                num_requests: int = 100) -> Dict:
        """Evaluate API performance under load."""
        logger.info(f"Evaluating API performance with {num_requests} requests...")
        
        test_urls = [
            "http://example.com",
            "https://google.com/search?q=test",
            "http://malicious-site.tk/login.php",
            "https://legitimate-bank.com/secure/login"
        ]
        
        # Test single requests
        single_request_times = []
        single_request_errors = 0
        
        for i in range(num_requests):
            url = np.random.choice(test_urls)
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{api_url}/detect",
                    json={"url": url},
                    timeout=10
                )
                response.raise_for_status()
                request_time = (time.time() - start_time) * 1000
                single_request_times.append(request_time)
            except Exception as e:
                single_request_errors += 1
                logger.warning(f"Request {i} failed: {e}")
                
        # Test concurrent requests
        concurrent_levels = [1, 5, 10, 20]
        concurrent_results = {}
        
        for concurrency in concurrent_levels:
            request_times = []
            errors = 0
            
            def make_request():
                url = np.random.choice(test_urls)
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{api_url}/detect",
                        json={"url": url},
                        timeout=10
                    )
                    response.raise_for_status()
                    return (time.time() - start_time) * 1000
                except Exception as e:
                    return None
                    
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(make_request) for _ in range(50)]
                
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        request_times.append(result)
                    else:
                        errors += 1
                        
            concurrent_results[concurrency] = {
                'mean_response_time_ms': np.mean(request_times) if request_times else 0,
                'p95_response_time_ms': np.percentile(request_times, 95) if request_times else 0,
                'success_rate': len(request_times) / 50,
                'errors': errors
            }
            
        return {
            'single_requests': {
                'mean_response_time_ms': np.mean(single_request_times) if single_request_times else 0,
                'median_response_time_ms': np.median(single_request_times) if single_request_times else 0,
                'p95_response_time_ms': np.percentile(single_request_times, 95) if single_request_times else 0,
                'success_rate': (num_requests - single_request_errors) / num_requests,
                'total_errors': single_request_errors
            },
            'concurrent_requests': concurrent_results
        }
        
    def run_full_evaluation(self, models_dir: str = "models", 
                          test_data_path: str = None) -> Dict:
        """Run complete evaluation suite."""
        logger.info("Starting comprehensive evaluation...")
        
        models_path = Path(models_dir)
        results = {}
        
        # Model accuracy evaluation
        if test_data_path and Path(test_data_path).exists():
            results['accuracy'] = self.evaluate_model_accuracy(
                models_path, Path(test_data_path)
            )
        
        # Performance evaluations
        results['latency'] = self.evaluate_inference_latency(models_path)
        results['memory'] = self.evaluate_memory_usage(models_path)
        
        # API evaluation (if API is running)
        try:
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code == 200:
                results['api_performance'] = self.evaluate_api_performance()
            else:
                logger.warning("API not available for performance testing")
        except Exception:
            logger.warning("API not available for performance testing")
            
        return results
        
    def save_results(self, results: Dict, output_path: Path):
        """Save evaluation results."""
        ensure_dir(output_path.parent)
        
        # Save JSON results
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        # Create human-readable report
        report_path = output_path.parent / "evaluation_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("Edge-AI Malicious URL Detection - Evaluation Report\n")
            f.write("=" * 60 + "\n\n")
            
            # Accuracy results
            if 'accuracy' in results:
                acc = results['accuracy']
                f.write("MODEL ACCURACY:\n")
                f.write(f"  Accuracy: {acc['accuracy']:.4f}\n")
                f.write(f"  Precision: {acc['precision']:.4f}\n")
                f.write(f"  Recall: {acc['recall']:.4f}\n")
                f.write(f"  F1-Score: {acc['f1_score']:.4f}\n")
                f.write(f"  ROC-AUC: {acc['roc_auc']:.4f}\n")
                f.write(f"  Test Samples: {acc['test_samples']}\n\n")
                
            # Latency results
            if 'latency' in results:
                lat = results['latency']['single_inference']
                f.write("INFERENCE LATENCY:\n")
                f.write(f"  Mean: {lat['mean_latency_ms']:.2f} ms\n")
                f.write(f"  Median: {lat['median_latency_ms']:.2f} ms\n")
                f.write(f"  95th percentile: {lat['p95_latency_ms']:.2f} ms\n")
                f.write(f"  99th percentile: {lat['p99_latency_ms']:.2f} ms\n\n")
                
            # Memory results
            if 'memory' in results:
                mem = results['memory']
                f.write("MEMORY USAGE:\n")
                f.write(f"  Model Loading: {mem['model_loading_memory_mb']:.2f} MB\n")
                f.write(f"  Total After Load: {mem['total_memory_after_load_mb']:.2f} MB\n")
                f.write(f"  Inference Overhead (mean): {mem['inference_memory_overhead_mb']['mean']:.2f} MB\n\n")
                
            # API performance
            if 'api_performance' in results:
                api = results['api_performance']['single_requests']
                f.write("API PERFORMANCE:\n")
                f.write(f"  Mean Response Time: {api['mean_response_time_ms']:.2f} ms\n")
                f.write(f"  95th percentile: {api['p95_response_time_ms']:.2f} ms\n")
                f.write(f"  Success Rate: {api['success_rate']:.2%}\n\n")
                
        logger.info(f"Evaluation results saved to {output_path}")
        logger.info(f"Human-readable report saved to {report_path}")

def main():
    """Main evaluation script."""
    logger.info("Starting Edge-AI evaluation...")
    
    evaluator = PerformanceEvaluator()
    
    # Run evaluation
    results = evaluator.run_full_evaluation(
        models_dir="models",
        test_data_path="data/processed/features_dataset.csv"  # Will use full dataset if test split not available
    )
    
    # Save results
    output_path = Path("reports/evaluation_results.json")
    evaluator.save_results(results, output_path)
    
    logger.info("Evaluation completed successfully!")

if __name__ == "__main__":
    main()