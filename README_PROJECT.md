# Edge-AI Real-Time Malicious Domain & URL Detection

## Project Structure
```
├── src/                          # Core source code
│   ├── data/                    # Data processing modules
│   ├── features/                # Feature extraction
│   ├── models/                  # ML models (RF, Transformer, GNN)
│   ├── api/                     # FastAPI endpoints
│   └── utils/                   # Utilities & helpers
├── config/                      # Configuration files
├── docker/                      # Docker services
├── notebooks/                   # Jupyter analysis
├── models/                      # Trained model artifacts
├── data/                        # Processed datasets
├── tests/                       # Unit tests
└── deployment/                  # Edge deployment scripts
```

## Datasets Available
1. **CSVs/CSV_phishing.csv** - 1,288 phishing domains with rich features
2. **CSVs/CSV_benign.csv** - 1,714 benign domains
3. **Malicious URLs dataset/malicious_phish.csv** - 651K URLs (phishing/benign/defacement)
4. **data_1/DNS_2m/** - 897K DNS domains with graph structure

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Build unified dataset
python scripts/build_dataset.py

# Extract features
python scripts/extract_features.py

# Train models
python scripts/train_models.py

# Run API
python -m src.api.main
```

## Architecture
- **Data Pipeline**: ETL → Feature Extraction → Model Training → Edge Deployment
- **Models**: Random Forest + Transformer + GNN ensemble
- **Deployment**: Docker Compose microservices on Edge Gateway