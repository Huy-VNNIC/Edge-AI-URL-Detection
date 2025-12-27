#!/usr/bin/env python3
"""
Ablation Study Framework
Tests different feature combinations to identify potential data leakage
Critical for validating that high performance is not due to metadata artifacts
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import cross_val_score
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Feature groups for ablation study
FEATURE_GROUPS = {
    "lexical_only": [
        "url_length", "url_entropy", "url_digit_ratio", "url_special_ratio",
        "has_https", "has_ip", "domain_length", "domain_entropy", 
        "num_subdomains", "domain_digit_ratio", "num_hyphens", 
        "num_underscores", "suspicious_tld", "domain_has_vowels",
        "path_length", "num_path_segments", "path_entropy", 
        "has_exe", "query_length", "num_query_params", "query_entropy",
        "is_shortened", "has_punycode", "obfuscated"
    ],
    
    "dns_features": [
        "ttl_normalized", "name_server_count", "mx_record_count"
    ],
    
    "whois_metadata": [
        "domain_age_days", "has_registrant", "registrant", 
        "has_organization", "organization", "registrar"
    ],
    
    "ranking_features": [
        "page_rank", "alexa_rank", "traffic_rank"
    ]
}

def load_feature_data():
    """Load extracted features for ablation study"""
    # Load both train and test features for full dataset ablation
    feature_files = [
        ("data/processed/train_features.csv", "data/processed/test_features.csv"),  # New split features
        "data/processed/features_dataset.csv",  # Original features
        "data/processed/features.csv"  # Fallback
    ]
    
    # Try to load train+test split features
    train_file, test_file = feature_files[0]
    if os.path.exists(train_file) and os.path.exists(test_file):
        logger.info(f"Loading split features from: {train_file} and {test_file}")
        train_df = pd.read_csv(train_file)
        test_df = pd.read_csv(test_file)
        combined_df = pd.concat([train_df, test_df], axis=0, ignore_index=True)
        return combined_df
    
    # Fallback to single files
    for file_path in feature_files[1:]:
        if os.path.exists(file_path):
            logger.info(f"Loading features from: {file_path}")
            return pd.read_csv(file_path)
    
    logger.error("No feature file found. Run feature extraction first.")
    return None

def prepare_feature_subsets(df: pd.DataFrame) -> dict:
    """Prepare different feature subset combinations"""
    available_features = [col for col in df.columns if col not in ['url', 'domain', 'label', 'source']]
    
    # Check which features are actually available
    feature_subsets = {}
    
    # Lexical only (core URL/domain features)
    lexical_available = [f for f in FEATURE_GROUPS["lexical_only"] if f in available_features]
    if lexical_available:
        feature_subsets["lexical_only"] = lexical_available
    
    # Lexical + DNS
    dns_available = [f for f in FEATURE_GROUPS["dns_features"] if f in available_features]
    if lexical_available and dns_available:
        feature_subsets["lexical_dns"] = lexical_available + dns_available
    
    # Lexical + WHOIS metadata
    whois_available = [f for f in FEATURE_GROUPS["whois_metadata"] if f in available_features]
    if lexical_available and whois_available:
        feature_subsets["lexical_whois"] = lexical_available + whois_available
    
    # Lexical + Ranking
    ranking_available = [f for f in FEATURE_GROUPS["ranking_features"] if f in available_features]
    if lexical_available and ranking_available:
        feature_subsets["lexical_ranking"] = lexical_available + ranking_available
    
    # Full feature set
    feature_subsets["full_hybrid"] = available_features
    
    # Metadata only (to test leakage)
    metadata_only = dns_available + whois_available + ranking_available
    if metadata_only:
        feature_subsets["metadata_only"] = metadata_only
    
    logger.info(f"Prepared {len(feature_subsets)} feature subsets:")
    for name, features in feature_subsets.items():
        logger.info(f"  {name}: {len(features)} features")
    
    return feature_subsets

def train_and_evaluate_model(X_train, y_train, X_test, y_test, feature_name: str):
    """Train Random Forest and evaluate performance"""
    # Use same parameters as main model for fair comparison
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    # Train model
    rf.fit(X_train, y_train)
    
    # Predictions
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0.5
    }
    
    # Feature importance
    feature_importance = dict(zip(X_train.columns, rf.feature_importances_))
    
    return metrics, feature_importance, rf

def cross_validation_evaluation(df: pd.DataFrame, feature_subsets: dict):
    """Perform cross-validation on different feature subsets"""
    logger.info("Running cross-validation ablation study...")
    
    cv_results = {}
    
    for subset_name, features in feature_subsets.items():
        logger.info(f"Evaluating {subset_name} ({len(features)} features)...")
        
        # Prepare data
        X = df[features].fillna(-1)  # Fill missing values
        y = df['label']
        
        # 5-fold cross-validation
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
        )
        
        # Multiple metrics
        scoring_metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        scores = {}
        
        for metric in scoring_metrics:
            cv_scores = cross_val_score(rf, X, y, cv=5, scoring=metric, n_jobs=-1)
            scores[metric] = {
                'mean': cv_scores.mean(),
                'std': cv_scores.std(),
                'scores': cv_scores.tolist()
            }
        
        cv_results[subset_name] = {
            'num_features': len(features),
            'features': features,
            'metrics': scores
        }
        
        logger.info(f"  {subset_name} - Accuracy: {scores['accuracy']['mean']:.4f} ± {scores['accuracy']['std']:.4f}")
    
    return cv_results

def main():
    """Main ablation study pipeline"""
    logger.info("Starting ablation study...")
    
    # Load feature data
    df = load_feature_data()
    if df is None:
        return
    
    logger.info(f"Loaded {len(df)} samples with {len([c for c in df.columns if c not in ['url', 'domain', 'label', 'source']])} features")
    
    # Prepare feature subsets
    feature_subsets = prepare_feature_subsets(df)
    if not feature_subsets:
        logger.error("No valid feature subsets could be prepared")
        return
    
    # Create output directory
    os.makedirs("data/ablation", exist_ok=True)
    
    # Method 1: Cross-validation ablation (robust but may not show train/test split effects)
    cv_results = cross_validation_evaluation(df, feature_subsets)
    
    # Save CV results
    with open("data/ablation/cv_ablation_results.json", "w") as f:
        json.dump(cv_results, f, indent=2)
    
    # Method 2: Train/Test split ablation (using pre-extracted features)
    split_results = None
    train_file = "data/processed/train_features.csv"
    test_file = "data/processed/test_features.csv"
    
    if os.path.exists(train_file) and os.path.exists(test_file):
        logger.info("Using pre-extracted train/test features for ablation...")
        
        # Load pre-extracted feature data
        train_feature_df = pd.read_csv(train_file)
        test_feature_df = pd.read_csv(test_file)
        
        split_results = {}
        
        for subset_name, features in feature_subsets.items():
            logger.info(f"Split evaluation: {subset_name}...")
            
            # Check if features exist
            available_features = [f for f in features if f in train_feature_df.columns]
            if not available_features:
                logger.warning(f"No features available for {subset_name} in split data")
                continue
            
            # Prepare train/test data
            X_train = train_feature_df[available_features].fillna(-1)
            y_train = train_feature_df['label']
            X_test = test_feature_df[available_features].fillna(-1)
            y_test = test_feature_df['label']
            
            # Train and evaluate
            metrics, feature_importance, model = train_and_evaluate_model(
                X_train, y_train, X_test, y_test, subset_name
            )
            
            split_results[subset_name] = {
                'num_features': len(available_features),
                'features': available_features,
                'metrics': metrics,
                'feature_importance': dict(sorted(feature_importance.items(), 
                                                key=lambda x: x[1], reverse=True)[:10])
            }
            
            logger.info(f"  {subset_name} - Test Accuracy: {metrics['accuracy']:.4f}, AUC: {metrics['roc_auc']:.4f}")
    else:
        logger.warning("Pre-extracted feature files not found, skipping train/test split ablation")
    
    # Save split results
    if split_results:
        with open("data/ablation/split_ablation_results.json", "w") as f:
            json.dump(split_results, f, indent=2)
    
    # Generate summary report
    generate_ablation_report(cv_results, split_results)

def generate_ablation_report(cv_results: dict, split_results: dict = None):
    """Generate comprehensive ablation study report"""
    
    print("\n" + "="*60)
    print("           ABLATION STUDY RESULTS")
    print("="*60)
    
    # Cross-validation results
    print("\n1. CROSS-VALIDATION RESULTS (5-fold)")
    print("-" * 50)
    print(f"{'Feature Set':<20} {'Features':<8} {'Accuracy':<12} {'F1-Score':<12} {'ROC-AUC':<12}")
    print("-" * 50)
    
    for subset_name, results in cv_results.items():
        metrics = results['metrics']
        acc = f"{metrics['accuracy']['mean']:.4f}±{metrics['accuracy']['std']:.3f}"
        f1 = f"{metrics['f1']['mean']:.4f}±{metrics['f1']['std']:.3f}"
        auc = f"{metrics['roc_auc']['mean']:.4f}±{metrics['roc_auc']['std']:.3f}"
        
        print(f"{subset_name:<20} {results['num_features']:<8} {acc:<12} {f1:<12} {auc:<12}")
    
    # Split results if available
    if split_results:
        print("\n2. TRAIN/TEST SPLIT RESULTS (Domain-based)")
        print("-" * 50)
        print(f"{'Feature Set':<20} {'Features':<8} {'Accuracy':<10} {'F1-Score':<10} {'ROC-AUC':<10}")
        print("-" * 50)
        
        for subset_name, results in split_results.items():
            metrics = results['metrics']
            print(f"{subset_name:<20} {results['num_features']:<8} {metrics['accuracy']:.4f}     {metrics['f1_score']:.4f}     {metrics['roc_auc']:.4f}")
        
        # Feature importance analysis
        print("\n3. TOP FEATURES BY SUBSET")
        print("-" * 40)
        
        for subset_name, results in split_results.items():
            if 'feature_importance' in results:
                print(f"\n{subset_name.upper()}:")
                for feature, importance in list(results['feature_importance'].items())[:5]:
                    print(f"  {feature}: {importance:.4f}")
    
    # Analysis and recommendations
    print("\n4. LEAKAGE ANALYSIS")
    print("-" * 30)
    
    if split_results:
        # Check for suspicious patterns
        lexical_performance = split_results.get('lexical_only', {}).get('metrics', {}).get('roc_auc', 0)
        full_performance = split_results.get('full_hybrid', {}).get('metrics', {}).get('roc_auc', 0)
        metadata_performance = split_results.get('metadata_only', {}).get('metrics', {}).get('roc_auc', 0.5)
        
        print(f"Lexical-only AUC: {lexical_performance:.4f}")
        print(f"Full hybrid AUC: {full_performance:.4f}")
        print(f"Metadata-only AUC: {metadata_performance:.4f}")
        
        improvement = full_performance - lexical_performance
        print(f"Improvement from metadata: {improvement:.4f}")
        
        if metadata_performance > 0.8:
            print("⚠️  WARNING: High metadata-only performance suggests potential leakage!")
        elif improvement > 0.1:
            print("⚠️  WARNING: Large improvement from metadata features - investigate further")
        elif lexical_performance > 0.85:
            print("✅ Good: Strong lexical features suggest genuine URL patterns")
        
    print("\n5. RECOMMENDATIONS FOR PAPER")
    print("-" * 35)
    print("• Report both lexical-only and full hybrid results")
    print("• Emphasize domain-based split methodology")
    print("• Discuss feature importance and interpretability")
    if split_results and split_results.get('metadata_only', {}).get('metrics', {}).get('roc_auc', 0.5) > 0.8:
        print("• Address potential metadata leakage in limitations section")
    print("• Include cross-validation results for robustness")

if __name__ == "__main__":
    main()