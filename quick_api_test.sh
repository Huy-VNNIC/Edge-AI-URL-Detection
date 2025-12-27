#!/bin/bash
# Quick API performance test for academic paper

echo "🎯 Edge-AI API Performance Test for Academic Paper"
echo "=================================================="

# Check if models exist
if [ ! -f "models/rf_model.joblib" ]; then
    echo "⚠️ Models not found. Training models..."
    python3 scripts/train_models.py
fi

# Start API server in background
echo "🚀 Starting API server..."
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for server to start
echo "⏳ Waiting for API to start..."
sleep 10

# Test if API is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API server is responding"
    
    # Run benchmark
    echo "📊 Running API benchmark..."
    python3 scripts/api_benchmark.py
    
    # Generate paper-ready summary
    echo ""
    echo "📋 PAPER-READY API METRICS:"
    echo "================================"
    python3 -c "
import json, sys
try:
    with open('reports/api_benchmark_results.json', 'r') as f:
        data = json.load(f)
    
    seq = data['sequential_performance']
    
    print(f'Mean API Latency: {seq[\"mean_latency_ms\"]:.2f} ms')
    print(f'P95 API Latency: {seq[\"p95_latency_ms\"]:.2f} ms') 
    print(f'Success Rate: {seq[\"success_rate\"]*100:.1f}%')
    print(f'API Throughput: {seq[\"throughput_req_per_sec\"]:.1f} req/sec')
    print(f'Edge Compliant: {\"YES\" if seq[\"p95_latency_ms\"] < 200 else \"NO\"}')
    
except Exception as e:
    print(f'Error reading results: {e}')
"
else
    echo "❌ API server failed to start"
fi

# Stop API server
echo "🛑 Stopping API server..."
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null

echo "✅ API performance test completed!"