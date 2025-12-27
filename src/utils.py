"""Utility functions for the Edge-AI URL detection system."""

import logging
import yaml
from pathlib import Path
import sys
import os

def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Create default config if not exists
        return create_default_config(config_path)

def create_default_config(config_path: str) -> dict:
    """Create default configuration."""
    default_config = {
        'data': {
            'raw_dirs': {
                'csvs': 'CSVs',
                'malicious_urls': 'Malicious URLs dataset',
                'dns_data': 'data_1/DNS_2m'
            },
            'processed': {
                'unified_dataset': 'data/processed/unified_dataset.csv',
                'features_dataset': 'data/processed/features_dataset.csv'
            }
        },
        'models': {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 20,
                'min_samples_split': 5,
                'class_weight': 'balanced'
            }
        },
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
            'reload': False,
            'log_level': 'info'
        }
    }
    
    # Save default config
    ensure_dir(Path(config_path).parent)
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    return default_config

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/system.log') if Path('logs').exists() else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)

def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path