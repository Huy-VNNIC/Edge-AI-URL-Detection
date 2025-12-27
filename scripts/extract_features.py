#!/usr/bin/env python3
"""
Extract comprehensive features from unified dataset.
Creates feature-engineered dataset ready for ML training.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')

from src.features import FeatureExtractor
from src.utils import load_config, setup_logging, ensure_dir

def main():
    """Main feature extraction pipeline."""
    logger = setup_logging()
    config = load_config()
    
    logger.info("Starting feature extraction process...")
    
    # Load unified dataset
    input_path = Path(config['data']['processed']['unified_dataset'])
    
    if not input_path.exists():
        logger.error(f"Unified dataset not found at {input_path}")
        logger.error("Please run scripts/build_dataset.py first")
        return
        
    logger.info(f"Loading dataset from {input_path}")
    df = pd.read_csv(input_path)
    
    # Initialize feature extractor
    extractor = FeatureExtractor()
    
    # Extract all features
    features_df = extractor.extract_all_features(df)
    
    # Create output directory
    output_path = Path(config['data']['processed']['features_dataset'])
    ensure_dir(output_path.parent)
    
    # Save features dataset
    features_df.to_csv(output_path, index=False)
    
    logger.info(f"Saved features dataset to {output_path}")
    logger.info(f"Features shape: {features_df.shape}")
    
    # Feature analysis
    feature_cols = [col for col in features_df.columns if col not in ['label', 'source']]
    logger.info(f"Total features extracted: {len(feature_cols)}")
    
    # Check for missing values
    missing_stats = features_df[feature_cols].isnull().sum()
    if missing_stats.sum() > 0:
        logger.warning(f"Missing values found in {(missing_stats > 0).sum()} features")
        
    # Basic feature statistics
    feature_stats = features_df[feature_cols].describe()
    
    # Save feature info
    info_path = output_path.parent / "features_info.txt"
    with open(info_path, 'w') as f:
        f.write(f"Feature extraction completed\n")
        f.write(f"Total features: {len(feature_cols)}\n")
        f.write(f"Dataset shape: {features_df.shape}\n")
        f.write(f"Label distribution:\n{features_df['label'].value_counts()}\n")
        f.write(f"\nFeature list:\n")
        for feature in feature_cols:
            f.write(f"  - {feature}\n")
            
    # Save detailed feature statistics
    stats_path = output_path.parent / "features_statistics.csv"
    feature_stats.to_csv(stats_path)
    
    logger.info(f"Saved feature info to {info_path}")
    logger.info(f"Saved feature statistics to {stats_path}")

if __name__ == "__main__":
    main()