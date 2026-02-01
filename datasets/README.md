# Dataset Information

This directory contains the datasets used for training and evaluating the Edge-AI malicious URL detection system.

## Directory Structure

- `original/` - Original raw datasets (not tracked in git due to size)
- `processed/` - Preprocessed and feature-engineered datasets

## Datasets Used

### Primary Dataset (100,000 URLs)
- **Malicious URLs**: 50,000 samples from URLhaus (https://urlhaus.abuse.ch/)
- **Benign URLs**: 50,000 samples from Majestic Million (https://majestic.com/reports/majestic-million)

### Additional Reference Datasets
- CIC Trap4Phish 2025 Dataset
- Malicious Domain Name Dataset (12 Features, 10,000 samples)
- Malicious URLs dataset

## Feature Extraction

31-dimensional feature framework:
- URL Lexical Features (12 features): length, entropy, special characters, etc.
- Domain Metadata (10 features): age, registration info, TLD characteristics
- DNS Features (5 features): query patterns, NXDOMAIN ratio
- SSL Features (4 features): certificate metadata, validity

## Data Splits

- Training: 70% (70,000 URLs)
- Validation: 15% (15,000 URLs)
- Testing: 15% (15,000 URLs)

Balanced across malicious/benign classes.

## Usage

Datasets are automatically downloaded and processed by running:

```bash
python scripts/build_dataset.py
```

Note: Large datasets are not included in the repository. Download links are provided in the main README.
