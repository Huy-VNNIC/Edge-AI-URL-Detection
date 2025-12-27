#!/usr/bin/env python3
"""
Extract features for expanded dataset
Handles multiple data sources and formats
"""

import pandas as pd
import argparse
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append('.')

from src.features import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Extract features from URL dataset')
    parser.add_argument('--input', default='data/splits/train_domain_split.csv', 
                       help='Input CSV file with URLs')
    parser.add_argument('--output', default='data/processed/train_features.csv',
                       help='Output CSV file for features')
    
    args = parser.parse_args()
    
    logger.info(f"Loading dataset from {args.input}")
    
    if not Path(args.input).exists():
        logger.error(f"Input file {args.input} does not exist")
        return
    
    # Load dataset
    df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(df)} URLs")
    
    # Ensure required columns
    required_cols = ['url', 'label']
    for col in required_cols:
        if col not in df.columns:
            logger.error(f"Required column '{col}' not found in dataset")
            return
    
    # Initialize feature extractor
    extractor = FeatureExtractor()
    
    # Extract features
    logger.info("Extracting features...")
    try:
        features_df = extractor.extract_all_features(df)
        
        # Ensure output directory exists
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        
        # Save features
        features_df.to_csv(args.output, index=False)
        logger.info(f"Saved {len(features_df)} feature records to {args.output}")
        
        # Print feature summary
        feature_cols = [col for col in features_df.columns if col not in ['url', 'domain', 'label', 'source']]
        logger.info(f"Extracted {len(feature_cols)} features")
        
        # Check for missing values
        missing_summary = features_df[feature_cols].isnull().sum()
        if missing_summary.sum() > 0:
            logger.warning("Features with missing values:")
            for feature, count in missing_summary[missing_summary > 0].items():
                logger.warning(f"  {feature}: {count} missing ({count/len(features_df)*100:.1f}%)")
        
        print(f"\n✓ Feature extraction completed successfully!")
        print(f"Input: {len(df)} URLs")
        print(f"Output: {len(features_df)} feature records")
        print(f"Features: {len(feature_cols)}")
        print(f"Saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()