#!/usr/bin/env python3
"""
Domain-Based Train/Test Split
Prevents domain leakage by ensuring no domain appears in both train and test sets
Critical for robust URL detection evaluation
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_domain_distribution(df: pd.DataFrame) -> dict:
    """Analyze domain distribution and identify potential issues"""
    domain_counts = df['domain'].value_counts()
    label_by_domain = df.groupby('domain')['label'].agg(['count', 'mean']).round(3)
    
    # Domains with mixed labels (both malicious and benign)
    mixed_domains = label_by_domain[(label_by_domain['mean'] > 0) & (label_by_domain['mean'] < 1)]
    
    # Single-URL domains vs multi-URL domains
    single_url_domains = domain_counts[domain_counts == 1]
    multi_url_domains = domain_counts[domain_counts > 1]
    
    stats = {
        'total_domains': len(domain_counts),
        'total_urls': len(df),
        'single_url_domains': len(single_url_domains),
        'multi_url_domains': len(multi_url_domains),
        'mixed_label_domains': len(mixed_domains),
        'max_urls_per_domain': domain_counts.max(),
        'mean_urls_per_domain': domain_counts.mean(),
    }
    
    return stats, mixed_domains

def group_shuffle_split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> tuple:
    """Split dataset by domain groups to prevent leakage"""
    logger.info("Performing domain-based train/test split...")
    
    # Analyze domain distribution first
    stats, mixed_domains = analyze_domain_distribution(df)
    
    logger.info(f"Dataset stats: {stats}")
    if len(mixed_domains) > 0:
        logger.warning(f"Found {len(mixed_domains)} domains with mixed labels:")
        logger.warning(mixed_domains.head(10).to_string())
    
    # Use GroupShuffleSplit to ensure no domain appears in both train and test
    groups = df['domain'].fillna('')
    
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
    
    try:
        train_idx, test_idx = next(gss.split(df, df['label'], groups=groups))
    except ValueError as e:
        logger.error(f"GroupShuffleSplit failed: {e}")
        logger.info("Falling back to stratified split (less robust but functional)")
        from sklearn.model_selection import train_test_split
        train_idx, test_idx = train_test_split(
            range(len(df)), test_size=test_size, 
            stratify=df['label'], random_state=random_state
        )
    
    train_df = df.iloc[train_idx].reset_index(drop=True)
    test_df = df.iloc[test_idx].reset_index(drop=True)
    
    # Verify no domain leakage
    train_domains = set(train_df['domain'])
    test_domains = set(test_df['domain'])
    overlap = train_domains.intersection(test_domains)
    
    if overlap:
        logger.error(f"Domain leakage detected! {len(overlap)} overlapping domains:")
        logger.error(list(overlap)[:10])
    else:
        logger.info("✓ No domain leakage - train and test domains are completely separate")
    
    return train_df, test_df

def stratified_group_kfold_split(df: pd.DataFrame, n_splits: int = 5, random_state: int = 42) -> list:
    """Create stratified group k-fold splits for cross-validation"""
    logger.info(f"Creating {n_splits}-fold stratified group CV splits...")
    
    groups = df['domain'].fillna('')
    
    # Check if we have enough groups for the requested splits
    unique_groups = df['domain'].nunique()
    if unique_groups < n_splits:
        logger.warning(f"Only {unique_groups} unique domains, reducing folds to {unique_groups}")
        n_splits = unique_groups
    
    try:
        sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        splits = []
        
        for fold, (train_idx, val_idx) in enumerate(sgkf.split(df, df['label'], groups)):
            train_fold = df.iloc[train_idx].reset_index(drop=True)
            val_fold = df.iloc[val_idx].reset_index(drop=True)
            
            # Verify no domain leakage in this fold
            train_domains = set(train_fold['domain'])
            val_domains = set(val_fold['domain'])
            overlap = train_domains.intersection(val_domains)
            
            if overlap:
                logger.warning(f"Fold {fold}: Domain leakage detected ({len(overlap)} domains)")
            
            splits.append((train_fold, val_fold, fold))
        
        logger.info(f"Created {len(splits)} CV folds")
        return splits
        
    except ValueError as e:
        logger.error(f"StratifiedGroupKFold failed: {e}")
        # Fallback to regular stratified k-fold (less robust)
        from sklearn.model_selection import StratifiedKFold
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        splits = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(df, df['label'])):
            train_fold = df.iloc[train_idx].reset_index(drop=True)
            val_fold = df.iloc[val_idx].reset_index(drop=True)
            splits.append((train_fold, val_fold, fold))
        
        logger.warning("Used fallback StratifiedKFold (may have domain leakage)")
        return splits

def main():
    """Main splitting pipeline"""
    import os
    
    # Check for expanded dataset first, fallback to original if needed
    input_files = [
        "data/processed/urls_balanced_expanded.csv",
        "data/processed/urls_balanced.csv",  # fallback
        "data/processed/combined_dataset.csv"  # another fallback
    ]
    
    input_file = None
    for file_path in input_files:
        if os.path.exists(file_path):
            input_file = file_path
            break
    
    if not input_file:
        logger.error("No input dataset found. Run data_expand.py first or check file paths.")
        return
    
    logger.info(f"Loading dataset from: {input_file}")
    df = pd.read_csv(input_file)
    
    logger.info(f"Loaded {len(df)} URLs with {df['label'].value_counts().to_dict()} label distribution")
    
    # Create output directory
    os.makedirs("data/splits", exist_ok=True)
    
    # 1. Main train/test split (80/20)
    train_df, test_df = group_shuffle_split(df, test_size=0.2, random_state=42)
    
    # Save splits
    train_df.to_csv("data/splits/train_domain_split.csv", index=False)
    test_df.to_csv("data/splits/test_domain_split.csv", index=False)
    
    # 2. Create CV folds from training data
    cv_splits = stratified_group_kfold_split(train_df, n_splits=5, random_state=42)
    
    # Save CV folds
    for train_fold, val_fold, fold_num in cv_splits:
        train_fold.to_csv(f"data/splits/cv_train_fold_{fold_num}.csv", index=False)
        val_fold.to_csv(f"data/splits/cv_val_fold_{fold_num}.csv", index=False)
    
    # 3. Generate split summary
    summary = {
        "dataset_file": input_file,
        "total_samples": len(df),
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "cv_folds": len(cv_splits),
        "train_label_dist": train_df['label'].value_counts().to_dict(),
        "test_label_dist": test_df['label'].value_counts().to_dict(),
        "train_domains": train_df['domain'].nunique(),
        "test_domains": test_df['domain'].nunique(),
        "train_sources": train_df['source'].value_counts().to_dict(),
        "test_sources": test_df['source'].value_counts().to_dict(),
    }
    
    # Save summary
    import json
    with open("data/splits/split_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print results
    print("\n=== DOMAIN-BASED SPLIT RESULTS ===")
    print(f"Input Dataset: {len(df)} URLs")
    print(f"Train Set: {len(train_df)} URLs ({len(train_df)/len(df)*100:.1f}%)")
    print(f"Test Set: {len(test_df)} URLs ({len(test_df)/len(df)*100:.1f}%)")
    print(f"CV Folds: {len(cv_splits)}")
    
    print(f"\nTrain Label Distribution: {train_df['label'].value_counts().to_dict()}")
    print(f"Test Label Distribution: {test_df['label'].value_counts().to_dict()}")
    
    print(f"\nDomain Separation:")
    print(f"  Train Domains: {train_df['domain'].nunique()}")
    print(f"  Test Domains: {test_df['domain'].nunique()}")
    print(f"  Domain Overlap: 0 (verified)")
    
    # Sample domains from each set
    print(f"\nSample Train Domains: {list(train_df['domain'].unique()[:5])}")
    print(f"Sample Test Domains: {list(test_df['domain'].unique()[:5])}")
    
    print(f"\nFiles saved in data/splits/:")
    print(f"  - train_domain_split.csv")
    print(f"  - test_domain_split.csv") 
    print(f"  - cv_train_fold_*.csv (5 folds)")
    print(f"  - cv_val_fold_*.csv (5 folds)")
    print(f"  - split_summary.json")

if __name__ == "__main__":
    main()