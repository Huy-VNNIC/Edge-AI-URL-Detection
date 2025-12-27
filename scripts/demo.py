#!/usr/bin/env python3
"""
Quick demo script to test the entire Edge-AI URL detection pipeline.
"""

import requests
import json
import time
import sys
from pathlib import Path

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Edge-AI URL Detection API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test single URL detection
    test_urls = [
        "https://google.com",
        "http://malicious-site.tk/login.php?redirect=evil",
        "https://github.com/microsoft/vscode",
        "http://192.168.1.1/admin.php",
        "https://shortened.ly/abc123"
    ]
    
    print("\n🔍 Single URL Detection Tests:")
    print("-" * 30)
    
    for url in test_urls:
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/detect",
                json={"url": url, "include_metadata": True}
            )
            response_time = (time.time() - start_time) * 1000
            
            result = response.json()
            
            print(f"URL: {url}")
            print(f"  Prediction: {result['label']} (confidence: {result['confidence']:.3f})")
            print(f"  Processing Time: {response_time:.2f}ms")
            print()
            
        except Exception as e:
            print(f"❌ Failed to test {url}: {e}")
    
    # Test batch detection
    print("\n📦 Batch URL Detection Test:")
    print("-" * 30)
    
    try:
        batch_urls = test_urls[:3]  # Test with 3 URLs
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/detect/batch",
            json={"urls": batch_urls, "include_metadata": True}
        )
        response_time = (time.time() - start_time) * 1000
        
        result = response.json()
        
        print(f"Batch of {len(batch_urls)} URLs:")
        print(f"  Total Processing Time: {response_time:.2f}ms")
        print(f"  Average per URL: {response_time/len(batch_urls):.2f}ms")
        
        for i, url_result in enumerate(result['results']):
            print(f"  {i+1}. {url_result['url']} -> {url_result['label']}")
            
    except Exception as e:
        print(f"❌ Batch test failed: {e}")
    
    return True

def run_pipeline_test():
    """Test the complete training pipeline."""
    print("\n🔄 Testing Training Pipeline...")
    print("=" * 50)
    
    # Check if models exist
    models_dir = Path("models")
    if models_dir.exists() and (models_dir / "rf_model.joblib").exists():
        print("✅ Models found - pipeline previously completed")
        return True
    
    print("🏗️ Running complete training pipeline...")
    
    # Import and run pipeline steps
    try:
        sys.path.append('.')
        
        # Step 1: Build dataset
        print("1️⃣ Building dataset...")
        from scripts.build_dataset import main as build_dataset
        build_dataset()
        
        # Step 2: Extract features  
        print("2️⃣ Extracting features...")
        from scripts.extract_features import main as extract_features
        extract_features()
        
        # Step 3: Train models
        print("3️⃣ Training models...")
        from scripts.train_models import main as train_models
        train_models()
        
        print("✅ Training pipeline completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🚀 Edge-AI Malicious URL Detection - Demo & Test")
    print("=" * 60)
    
    # Test training pipeline first
    pipeline_success = run_pipeline_test()
    
    if not pipeline_success:
        print("\n❌ Training pipeline failed. Cannot proceed with API tests.")
        return
    
    # Test API
    print("\n" + "="*60)
    print("Starting API server test...")
    print("Note: Make sure API is running with: python -m src.api.main")
    print("Or with Docker: docker-compose up -d edge-ai-api")
    
    input("\nPress Enter when API is ready...")
    
    api_success = test_api_endpoints()
    
    if api_success:
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Check the following directories for results:")
        print("  - models/: Trained ML models")
        print("  - reports/: Training metrics and plots")  
        print("  - data/processed/: Processed datasets")
        
        print("\n🔗 API Endpoints:")
        print("  - http://localhost:8000/: API documentation")
        print("  - http://localhost:8000/health: Health check")
        print("  - http://localhost:8000/detect: Single URL detection")
        print("  - http://localhost:8000/detect/batch: Batch URL detection")
        
        if Path("docker-compose.yml").exists():
            print("\n🐳 Docker Services:")
            print("  - Grafana Dashboard: http://localhost:3000 (admin/admin123)")
            print("  - Prometheus Metrics: http://localhost:9090")
    else:
        print("\n❌ API tests failed. Check if the API server is running.")

if __name__ == "__main__":
    main()