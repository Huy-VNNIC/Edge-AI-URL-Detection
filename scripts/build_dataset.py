#!/usr/bin/env python3
"""
Build unified dataset from all available sources.
Combines CSV datasets, malicious URLs, and DNS data.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')

from src.data import DataLoader
from src.utils import load_config, setup_logging, ensure_dir

def main():
    """Main dataset building pipeline."""
    logger = setup_logging()
    config = load_config()
    
    logger.info("Starting dataset building process...")
    
    # Initialize data loader
    loader = DataLoader()
    
    # Load all datasets
    df = loader.load_all_datasets()
    
    if df.empty:
        logger.error("No data loaded. Exiting.")
        return
        
    # Create output directory
    output_path = Path(config['data']['processed']['unified_dataset'])
    ensure_dir(output_path.parent)
    
    # Save unified dataset
    df.to_csv(output_path, index=False)
    
    logger.info(f"Saved unified dataset to {output_path}")
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Label distribution:")
    logger.info(df['label'].value_counts())
    logger.info(f"Source distribution:")
    logger.info(df['source'].value_counts())
    
    # Create basic statistics
    stats = {
        'total_records': len(df),
        'malicious_records': (df['label'] == 1).sum(),
        'benign_records': (df['label'] == 0).sum(),
        'sources': df['source'].unique().tolist(),
        'columns': df.columns.tolist()
    }
    
    stats_path = output_path.parent / "dataset_stats.txt"
    with open(stats_path, 'w') as f:
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")
            
    logger.info(f"Saved dataset statistics to {stats_path}")

if __name__ == "__main__":
    main()