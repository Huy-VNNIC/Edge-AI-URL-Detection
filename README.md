# Edge-AI Malicious URL Detection for IoT Gateway Security

A lightweight, deployment-ready machine learning system for detecting malicious URLs and domains at the IoT gateway edge. This system achieves 72.30% accuracy with only 3.5 MB memory footprint and 10.50 ms end-to-end latency, making it suitable for resource-constrained edge devices.

## System Architecture

<p align="center">
  <img src="https://res.cloudinary.com/dh41tyuha/image/upload/v1761564847/Screenshot_from_2025-10-27_20-33-13_aydcbw.png" alt="System Architecture" width="800"/>
</p>

### Data Flow Pipeline

```
URL Input → Feature Extraction → Normalization → Random Forest → Decision
  (0ms)         (3.19ms)           (0ms)          (7.31ms)      (10.50ms total)
```

See [detailed architecture documentation](docs/architecture.md) for component specifications and deployment modes.

## Overview

Traditional cloud-based URL detection systems introduce unacceptable latency and privacy concerns for IoT deployments. This project implements a complete Edge-AI solution that processes URLs locally at the gateway level, providing real-time threat detection without requiring cloud connectivity.

### Key Features

- Real-time malicious URL detection at IoT gateways
- Lightweight Random Forest model (1.8 MB model size, 3.5 MB memory usage)
- Fast inference (7.31 ms model prediction, 10.50 ms end-to-end)
- 31-dimensional feature engineering framework
- Containerized deployment with Docker support
- RESTful API for easy integration
- Comprehensive evaluation across 5 ML algorithms
- Production-ready with monitoring and logging

## Performance Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 72.30% |
| F1-Score | 0.7089 |
| Precision | 0.7156 |
| Recall | 0.7023 |
| Model Prediction Time | 7.31 ms |
| Feature Extraction Time | 3.19 ms |
| End-to-End Latency | 10.50 ms |
| Memory Footprint | 3.5 MB |
| Model Size | 1.8 MB |
| Throughput | 137 samples/sec |

## System Architecture

The system consists of four main components:

1. **Feature Extraction Module**: Extracts 31 features from URLs including lexical patterns, DNS metadata, SSL certificate information, and domain registration data

2. **ML Detection Engine**: Random Forest classifier optimized for edge deployment with minimal resource requirements

3. **RESTful API**: FastAPI-based service exposing prediction endpoints for integration with network security infrastructure

4. **Monitoring Stack**: Prometheus metrics collection and logging for production deployment

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- 512 MB RAM minimum (recommended: 1 GB)
- Linux-based system (tested on Ubuntu 20.04+)

### Quick Start

1. Clone the repository:

```bash
git clone https://github.com/Huy-VNNIC/Edge-AI-URL-Detection.git
cd Edge-AI-URL-Detection
```

2. Create and activate virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download datasets and build features:

```bash
python scripts/build_dataset.py
python scripts/extract_features.py
```

5. Train the model:

```bash
python scripts/train_model.py
```

## Usage

### Python API

```python
from src.models.predictor import URLPredictor

# Initialize predictor
predictor = URLPredictor(model_path='models/rf_model.joblib')

# Predict single URL
url = "http://suspicious-domain.com/malware.exe"
result = predictor.predict(url)
print(f"Malicious probability: {result['probability']:.2f}")
print(f"Prediction: {result['prediction']}")

# Batch prediction
urls = ["http://example.com", "http://phishing-site.ru/login"]
results = predictor.predict_batch(urls)
```

### REST API

Start the API server:

```bash
python src/api/main.py
```

Make predictions via HTTP:

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://suspicious-domain.com/malware.exe"}'
```

Response:

```json
{
  "url": "http://suspicious-domain.com/malware.exe",
  "prediction": "malicious",
  "probability": 0.87,
  "processing_time_ms": 10.2,
  "features": {
    "url_length": 45,
    "entropy": 3.42,
    "has_ip": false
  }
}
```

### Docker Deployment

Deploy the complete system with Docker Compose:

```bash
docker-compose up -d
```

This starts:
- API service on port 8000
- Prometheus metrics on port 9090

Check service health:

```bash
curl http://localhost:8000/health
```

## Configuration

Edit `config/config.yaml` to customize system behavior:

```yaml
model:
  type: "random_forest"
  path: "models/rf_model.joblib"
  threshold: 0.5

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4

feature_extraction:
  timeout: 5
  dns_resolution: true
  ssl_verification: true

logging:
  level: "INFO"
  file: "logs/detection.log"
```

## Project Structure

```
Edge-AI-URL-Detection/
├── config/                  # Configuration files
│   └── config.yaml         # System configuration
│
├── datasets/               # Dataset storage (not in git)
│   ├── original/          # Raw datasets
│   │   ├── cic_trap4phish/           # CIC Trap4Phish 2025
│   │   ├── malicious_domain_features/ # 12-feature domain dataset
│   │   ├── malicious_phish_dataset/   # Malicious phish URLs
│   │   ├── base_json/                 # Base JSON datasets
│   │   ├── CSV_benign.csv            # Benign URL samples
│   │   ├── CSV_malware.csv           # Malware URL samples
│   │   ├── CSV_phishing.csv          # Phishing URL samples
│   │   └── CSV_spam.csv              # Spam URL samples
│   └── processed/         # Processed features and splits
│       ├── features/      # Extracted feature sets
│       └── splits/        # Train/validation/test splits
│
├── data/                  # Working data directories
│   ├── ablation/         # Ablation study results
│   ├── hashed_domain_names/
│   ├── processed/        # Processing outputs
│   ├── regular_domain_names/
│   └── splits/           # Dataset splits
│
├── deployment/           # Deployment configurations
│
├── docker/              # Docker containerization
│   ├── Dockerfile.api           # API service container
│   ├── Dockerfile.processor     # Processing service container
│   └── prometheus.yml           # Prometheus monitoring config
│
├── docs/                # Documentation
│   └── architecture.md  # System architecture details
│
├── models/              # Trained ML models
│   ├── rf_model.joblib         # Random Forest model
│   ├── rf_scaler.joblib        # Feature scaler
│   ├── rf_features.txt         # Feature names
│   └── test/                   # Test models
│
├── notebooks/           # Jupyter notebooks for analysis
│
├── paper/              # FJCAI 2026 Research Paper
│   ├── latex/         # LaTeX source files
│   └── img/           # Paper figures
│
├── reports/            # Evaluation reports and metrics
│   ├── api_benchmark_results.json
│   ├── evaluation_results.json
│   ├── paper_metrics_complete.json
│   └── cv_evaluation/         # Cross-validation results
│
├── scripts/            # Training and evaluation scripts
│   ├── build_dataset.py            # Dataset construction
│   ├── extract_features.py         # Feature extraction
│   ├── train_model.py             # Model training
│   ├── evaluate_system.py         # System evaluation
│   ├── comprehensive_cv.py        # Cross-validation
│   ├── api_benchmark.py           # API performance test
│   ├── feature_importance_analysis.py
│   └── ablation_study.py          # Ablation experiments
│
├── src/                # Source code
│   ├── api/           # REST API implementation (FastAPI)
│   ├── data/          # Data processing pipelines
│   ├── features/      # Feature extraction modules
│   ├── models/        # ML model implementations
│   └── utils/         # Utility functions
│
├── tests/             # Unit and integration tests
│
├── docker-compose.yml # Docker Compose configuration
├── requirements.txt   # Python dependencies
├── .gitignore        # Git ignore patterns
├── LICENSE           # MIT License
└── README.md         # This file
```

## Feature Engineering

The system implements a 31-dimensional feature framework:

### URL Lexical Features (12 features)
- URL length, path length, query length
- Character entropy
- Digit ratio, special character ratio
- Presence of IP address
- URL structure indicators

### Domain Metadata Features (10 features)
- Domain age
- Registration period
- TLD characteristics
- WHOIS information
- Domain reputation metrics

### DNS Features (5 features)
- DNS query response time
- NXDOMAIN ratio
- TTL values
- A record count
- Fast-flux indicators

### SSL/TLS Features (4 features)
- Certificate validity period
- Certificate age
- Issuer information
- Subject Alternative Names count

## Model Comparison

The system was evaluated with 5 different ML algorithms:

| Model | Accuracy | F1-Score | Prediction Time | Memory | Throughput |
|-------|----------|----------|----------------|---------|-----------|
| Random Forest | 72.30% | 0.7089 | 7.31 ms | 3.5 MB | 137 samples/s |
| Logistic Regression | 72.37% | 0.7065 | 2.45 ms | 0.8 MB | 408 samples/s |
| Neural Network | 72.03% | 0.7050 | 3.12 ms | 1.5 MB | 321 samples/s |
| SVM | 71.80% | 0.6875 | 8.95 ms | 1.2 MB | 112 samples/s |
| XGBoost | 63.57% | 0.4941 | 4.28 ms | 2.1 MB | 234 samples/s |

Random Forest was selected for deployment due to optimal balance between accuracy, resource efficiency, and interpretability.

## Deployment Guidelines

### Hardware Requirements

Minimum:
- CPU: ARM Cortex-A53 or equivalent
- RAM: 512 MB
- Storage: 10 MB (model + dependencies)

Recommended:
- CPU: ARM Cortex-A72 or x86-64
- RAM: 1 GB
- Storage: 50 MB

### Tested Platforms

- Raspberry Pi 4 (4GB RAM)
- NVIDIA Jetson Nano
- AWS EC2 t3.micro
- Ubuntu 20.04 LTS / 22.04 LTS
- Docker containers

### Integration Scenarios

1. **DNS Resolver Integration**: Inline filtering at DNS level
2. **Firewall Mode**: Block/alert based on detection scores
3. **SIEM Integration**: Forward detections to Splunk/ELK
4. **Proxy Mode**: HTTP/HTTPS traffic inspection

## Evaluation and Ablation Studies

### Feature Ablation Results

| Configuration | Accuracy | F1-Score | Feature Count | Extraction Time |
|--------------|----------|----------|---------------|----------------|
| Full (31 features) | 72.30% | 0.7089 | 31 | 3.19 ms |
| Without DNS | 71.95% | 0.7045 | 26 | 2.87 ms |
| Without SSL | 71.42% | 0.6982 | 28 | 2.94 ms |
| URL + Domain Only | 69.73% | 0.6782 | 19 | 2.12 ms |
| Lexical Only | 65.24% | 0.6142 | 12 | 1.48 ms |

### Failure Analysis

Common false negative patterns:
- Sophisticated phishing with domain mimicry
- Legitimate-looking URLs with malicious payloads
- Fresh domains with no historical data
- Parameter-level obfuscation (Base64, hex encoding)

Common false positive patterns:
- Developer tools and CDN URLs
- API documentation with extensive parameters
- Regional TLDs (.ru, .cn) for legitimate sites

## Research Publication

This work has been accepted for publication at FJCAI 2026 (Conference on Artificial Intelligence):

**Title**: Edge-AI Malicious Domain and URL Detection for IoT Gateway Security: A Lightweight Random Forest Approach

**Authors**: Tung Phan Luu, Huy Nguyen Nhat, Bao Tran Minh, Gia Nhu Nguyen

**Paper ID**: 157

Camera-ready paper available in `paper/latex/main.pdf`

## Testing

Run unit tests:

```bash
pytest tests/
```

Run integration tests:

```bash
python tests/test_api.py
python tests/test_pipeline.py
```

Performance benchmarking:

```bash
python scripts/api_benchmark.py
```

## Monitoring and Logging

### Prometheus Metrics

Available at `http://localhost:9090/metrics`:

- `url_detection_requests_total`: Total prediction requests
- `url_detection_latency_seconds`: Request latency histogram
- `url_detection_malicious_total`: Malicious URL count
- `model_inference_time_seconds`: Model prediction time

### Log Files

- Application logs: `logs/detection.log`
- API access logs: `logs/api_access.log`
- Error logs: `logs/errors.log`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- New features include unit tests
- Documentation is updated

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@inproceedings{luu2026edge,
  title={Edge-AI Malicious Domain and URL Detection for IoT Gateway Security: A Lightweight Random Forest Approach},
  author={Luu, Tung Phan and Nguyen, Huy Nhat and Tran, Bao Minh and Nguyen, Gia Nhu},
  booktitle={Proceedings of the Conference on Artificial Intelligence (FJCAI)},
  year={2026}
}
```

## Acknowledgments

- URLhaus (abuse.ch) for malicious URL dataset
- Majestic Million for benign URL dataset
- FJCAI 2026 conference organizers and reviewers

## Contact

- Author: Huy Nguyen Nhat
- Email: nguyennhathuy11@dtu.edu.vn
- GitHub: https://github.com/Huy-VNNIC
- Repository: https://github.com/Huy-VNNIC/Edge-AI-URL-Detection

## Roadmap

Future enhancements planned:

- Real-time model updates via federated learning
- Adversarial robustness improvements
- Extended feature set for zero-day detection
- Support for additional IoT gateway platforms
- Web-based management interface
- Automated retraining pipeline

## Related Projects

- URLNet: Character-level CNN for URL classification
- PhishDef: URL-based phishing detection
- BERT-URL: Transformer-based URL analysis

## Changelog

### Version 1.0.0 (February 2026)
- Initial release
- Random Forest implementation with 31 features
- RESTful API with FastAPI
- Docker containerization
- FJCAI 2026 camera-ready paper

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Email the maintainers
- Check documentation in the `paper/` directory

## Security Notice

This system is designed as a defense-in-depth component and should not be relied upon as the sole security measure. Always deploy multiple layers of security controls in production environments.

## Disclaimer

The accuracy metrics reported (72.30%) reflect realistic performance under challenging cybersecurity conditions including label noise and edge deployment constraints. Performance may vary depending on the threat landscape and deployment environment. Regular model retraining is recommended.
