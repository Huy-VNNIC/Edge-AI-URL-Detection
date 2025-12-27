#!/bin/bash
# Edge-AI URL Detection - Quick Start Script

echo "🚀 Edge-AI Malicious URL Detection - Quick Start"
echo "================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/processed
mkdir -p models  
mkdir -p reports
mkdir -p logs

echo "✅ Dependencies installed"

# Run the complete pipeline
echo ""
echo "🏗️ Building dataset from existing sources..."
python scripts/build_dataset.py

echo ""
echo "🔧 Extracting features..."
python scripts/extract_features.py

echo ""
echo "🤖 Training ML models..."
python scripts/train_models.py

echo ""
echo "📊 Running evaluation..."
python scripts/evaluate_system.py

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Start the API server:"
echo "   python -m src.api.main"
echo ""
echo "2. Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "3. Test the system:"
echo "   python scripts/demo.py"
echo ""
echo "4. Access services:"
echo "   - API: http://localhost:8000"
echo "   - Grafana: http://localhost:3000 (admin/admin123)"
echo "   - Prometheus: http://localhost:9090"