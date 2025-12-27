#!/usr/bin/env python3
"""
Train all ML models on the feature-engineered dataset.
Trains Random Forest, Transformer, and GNN models as per architecture design.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')

from src.models import RandomForestModel, ModelEvaluator, TRANSFORMER_AVAILABLE, GNN_AVAILABLE
if TRANSFORMER_AVAILABLE:
    from src.models import TransformerModel
if GNN_AVAILABLE:
    from src.models import GNNModel
from src.utils import load_config, setup_logging, ensure_dir

def main():
    """Main model training pipeline."""
    logger = setup_logging()
    config = load_config()
    
    logger.info("Starting model training process...")
    
    # Load features dataset
    features_path = Path(config['data']['processed']['features_dataset'])
    
    if not features_path.exists():
        logger.error(f"Features dataset not found at {features_path}")
        logger.error("Please run scripts/extract_features.py first")
        return
        
    logger.info(f"Loading features from {features_path}")
    df = pd.read_csv(features_path)
    
    # Prepare data
    feature_cols = [col for col in df.columns if col not in ['label', 'source']]
    X = df[feature_cols].values
    y = df['label'].values
    
    logger.info(f"Dataset shape: {X.shape}")
    logger.info(f"Features: {len(feature_cols)}")
    logger.info(f"Label distribution: {np.bincount(y)}")
    
    # Handle missing values
    if np.isnan(X).any():
        logger.warning("Found NaN values, filling with 0")
        X = np.nan_to_num(X, 0)
        
    # Create output directories
    models_dir = Path("models")
    ensure_dir(models_dir)
    
    reports_dir = Path("reports")
    ensure_dir(reports_dir)
    
    # Initialize evaluator
    evaluator = ModelEvaluator(reports_dir)
    
    # Train Random Forest
    logger.info("Training Random Forest...")
    rf_model = RandomForestModel(config)
    rf_metrics = rf_model.train(X, y, feature_cols)
    
    # Save Random Forest model
    rf_model.save(models_dir)
    
    # Evaluate Random Forest
    X_test_split = X[int(0.8 * len(X)):]  # Approximate test split for visualization
    y_test_split = y[int(0.8 * len(y)):]
    
    y_pred_rf, y_prob_rf = rf_model.predict(X_test_split)
    
    # Generate evaluation plots and reports
    evaluator.plot_confusion_matrix(y_test_split, y_pred_rf, "Random Forest")
    evaluator.plot_feature_importance(rf_metrics['feature_importance'], "Random Forest")
    evaluator.save_metrics_report(rf_metrics, "Random Forest")
    
    logger.info("✅ Random Forest training completed")
    
    # Train Transformer model if available
    transformer_metrics = None
    if TRANSFORMER_AVAILABLE:
        try:
            logger.info("Training Transformer model...")
            transformer_config = config.get('models', {}).get('transformer', {
                'max_length': 256,
                'embed_dim': 128,
                'num_heads': 8,
                'num_layers': 4,
                'dropout': 0.1,
                'batch_size': 32,
                'epochs': 10,
                'learning_rate': 0.001
            })
            
            transformer_model = TransformerModel({'transformer': transformer_config})
            
            # Use original dataframe with URLs for transformer
            if 'url' in df.columns:
                transformer_metrics = transformer_model.train(df)
                transformer_model.save(models_dir)
                logger.info("✅ Transformer training completed")
            else:
                logger.warning("No URL column found for Transformer training")
                
        except Exception as e:
            logger.error(f"Transformer training failed: {e}")
    else:
        logger.info("⚠️ Transformer model not available (missing dependencies)")
    
    # Train GNN model if available
    gnn_metrics = None
    if GNN_AVAILABLE:
        try:
            logger.info("Training GNN model...")
            gnn_config = config.get('models', {}).get('gnn', {
                'hidden_dim': 64,
                'num_layers': 2,
                'dropout': 0.1,
                'batch_size': 1,
                'epochs': 50,
                'learning_rate': 0.001
            })
            
            gnn_model = GNNModel({'gnn': gnn_config})
            
            # Use original dataframe with URLs for GNN
            if 'url' in df.columns:
                gnn_metrics = gnn_model.train(df)
                gnn_model.save(models_dir)
                logger.info("✅ GNN training completed")
            else:
                logger.warning("No URL column found for GNN training")
                
        except Exception as e:
            logger.error(f"GNN training failed: {e}")
    else:
        logger.info("⚠️ GNN model not available (missing dependencies)")
    
    # Create comprehensive training summary
    training_summary = {
        'dataset_info': {
            'total_samples': len(df),
            'total_features': len(feature_cols),
            'benign_samples': (y == 0).sum(),
            'malicious_samples': (y == 1).sum(),
        },
        'random_forest': {
            'status': 'completed',
            'metrics': rf_metrics
        },
        'transformer': {
            'status': 'completed' if transformer_metrics else 'failed/unavailable',
            'metrics': transformer_metrics
        },
        'gnn': {
            'status': 'completed' if gnn_metrics else 'failed/unavailable', 
            'metrics': gnn_metrics
        }
    }
    
    # Summary report
    summary_path = reports_dir / "training_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("Multi-Model Training Summary\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Dataset Information:\n")
        f.write(f"  Total samples: {training_summary['dataset_info']['total_samples']}\n")
        f.write(f"  Features: {training_summary['dataset_info']['total_features']}\n")
        f.write(f"  Benign samples: {training_summary['dataset_info']['benign_samples']}\n")
        f.write(f"  Malicious samples: {training_summary['dataset_info']['malicious_samples']}\n\n")
        
        # Random Forest Results
        f.write("Random Forest Results:\n")
        rf_results = training_summary['random_forest']
        if rf_results['status'] == 'completed':
            f.write(f"  Status: ✅ {rf_results['status']}\n")
            f.write(f"  Accuracy: {rf_results['metrics']['accuracy']:.4f}\n")
            f.write(f"  ROC-AUC: {rf_results['metrics']['roc_auc']:.4f}\n")
        else:
            f.write(f"  Status: ❌ {rf_results['status']}\n")
        f.write("\n")
        
        # Transformer Results
        f.write("Transformer Results:\n")
        tf_results = training_summary['transformer']
        if tf_results['status'] == 'completed' and tf_results['metrics']:
            f.write(f"  Status: ✅ {tf_results['status']}\n")
            f.write(f"  Accuracy: {tf_results['metrics']['accuracy']:.4f}\n")
            f.write(f"  ROC-AUC: {tf_results['metrics']['roc_auc']:.4f}\n")
        else:
            f.write(f"  Status: ⚠️ {tf_results['status']}\n")
        f.write("\n")
        
        # GNN Results
        f.write("GNN Results:\n")
        gnn_results = training_summary['gnn']
        if gnn_results['status'] == 'completed' and gnn_results['metrics']:
            f.write(f"  Status: ✅ {gnn_results['status']}\n")
            f.write(f"  Accuracy: {gnn_results['metrics']['accuracy']:.4f}\n")
            f.write(f"  ROC-AUC: {gnn_results['metrics']['roc_auc']:.4f}\n")
            f.write(f"  Graph Stats: {gnn_results['metrics']['num_nodes']} nodes, {gnn_results['metrics']['num_edges']} edges\n")
        else:
            f.write(f"  Status: ⚠️ {gnn_results['status']}\n")
        f.write("\n")
        
        # Top Random Forest features (if available)
        if rf_results['status'] == 'completed' and 'feature_importance' in rf_results['metrics']:
            f.write("Top 10 Most Important Features (Random Forest):\n")
            top_features = sorted(rf_results['metrics']['feature_importance'].items(), 
                                key=lambda x: x[1], reverse=True)[:10]
            for feature, importance in top_features:
                f.write(f"  {feature}: {importance:.4f}\n")
    
    logger.info(f"🎉 Multi-model training completed! Summary saved to {summary_path}")
    logger.info(f"📁 Models saved to {models_dir}")
    logger.info(f"📊 Reports saved to {reports_dir}")
    
    # Log ensemble info
    models_trained = []
    if training_summary['random_forest']['status'] == 'completed':
        models_trained.append('Random Forest')
    if training_summary['transformer']['status'] == 'completed':
        models_trained.append('Transformer') 
    if training_summary['gnn']['status'] == 'completed':
        models_trained.append('GNN')
    
    logger.info(f"🤖 Ensemble models available: {', '.join(models_trained)}")

if __name__ == "__main__":
    main()