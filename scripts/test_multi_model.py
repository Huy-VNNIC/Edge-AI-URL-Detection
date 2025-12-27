#!/usr/bin/env python3
"""
Test multi-model training pipeline with small dataset
Tests Random Forest, Transformer, and GNN models
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')

from src.models import RandomForestModel, TRANSFORMER_AVAILABLE, GNN_AVAILABLE
if TRANSFORMER_AVAILABLE:
    from src.models import TransformerModel
if GNN_AVAILABLE:
    from src.models import GNNModel
from src.utils import load_config, setup_logging, ensure_dir

def test_multi_model_training():
    """Test training pipeline with all available models"""
    logger = setup_logging()
    logger.info("🧪 Testing multi-model training pipeline...")
    
    # Load small sample of data for testing
    data_file = "data/processed/urls_full_expanded.csv"
    
    if not Path(data_file).exists():
        logger.error(f"Dataset not found at {data_file}")
        return False
    
    # Load small sample for testing (1000 samples)
    logger.info(f"Loading sample data from {data_file}...")
    df = pd.read_csv(data_file, nrows=1000)
    
    logger.info(f"Loaded {len(df)} samples for testing")
    logger.info(f"Columns: {df.columns.tolist()}")
    logger.info(f"Label distribution:\n{df['label'].value_counts()}")
    
    # Create test directories
    test_models_dir = Path("models/test")
    test_reports_dir = Path("reports/test")
    ensure_dir(test_models_dir)
    ensure_dir(test_reports_dir)
    
    config = {
        'models': {
            'random_forest': {
                'n_estimators': 10,  # Smaller for testing
                'max_depth': 5,
                'min_samples_split': 5,
                'class_weight': 'balanced'
            },
            'transformer': {
                'max_length': 128,   # Smaller for testing
                'embed_dim': 64,
                'num_heads': 4,
                'num_layers': 2,
                'dropout': 0.1,
                'batch_size': 16,
                'epochs': 3,         # Fewer epochs for testing
                'learning_rate': 0.001
            },
            'gnn': {
                'hidden_dim': 32,    # Smaller for testing
                'num_layers': 2,
                'dropout': 0.1,
                'batch_size': 1,
                'epochs': 10,        # Fewer epochs for testing
                'learning_rate': 0.001
            }
        }
    }
    
    results = {}
    
    # Test 1: Random Forest (baseline)
    logger.info("\n🌲 Testing Random Forest...")
    try:
        # Extract features for RF (need numerical features)
        from src.features import FeatureExtractor
        extractor = FeatureExtractor()
        
        # Extract features
        features_df = extractor.extract_all_features(df)
        
        # Prepare RF data
        feature_cols = [col for col in features_df.columns if col not in ['url', 'domain', 'label', 'source']]
        X = features_df[feature_cols].fillna(-1).values
        y = features_df['label'].values
        
        rf_model = RandomForestModel(config)
        rf_metrics = rf_model.train(X, y, feature_cols)
        rf_model.save(test_models_dir)
        
        results['random_forest'] = {
            'status': 'success',
            'accuracy': rf_metrics['accuracy'],
            'roc_auc': rf_metrics['roc_auc']
        }
        logger.info(f"✅ Random Forest: Accuracy={rf_metrics['accuracy']:.4f}, AUC={rf_metrics['roc_auc']:.4f}")
        
    except Exception as e:
        logger.error(f"❌ Random Forest failed: {e}")
        results['random_forest'] = {'status': 'failed', 'error': str(e)}
    
    # Test 2: Transformer
    logger.info("\n🤖 Testing Transformer...")
    if TRANSFORMER_AVAILABLE:
        try:
            transformer_model = TransformerModel(config)
            transformer_metrics = transformer_model.train(df)
            transformer_model.save(test_models_dir)
            
            results['transformer'] = {
                'status': 'success',
                'accuracy': transformer_metrics['accuracy'],
                'roc_auc': transformer_metrics['roc_auc']
            }
            logger.info(f"✅ Transformer: Accuracy={transformer_metrics['accuracy']:.4f}, AUC={transformer_metrics['roc_auc']:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Transformer failed: {e}")
            results['transformer'] = {'status': 'failed', 'error': str(e)}
    else:
        results['transformer'] = {'status': 'unavailable', 'reason': 'Missing dependencies'}
        logger.info("⚠️ Transformer unavailable (missing PyTorch)")
    
    # Test 3: GNN
    logger.info("\n🕸️ Testing GNN...")
    if GNN_AVAILABLE:
        try:
            gnn_model = GNNModel(config)
            gnn_metrics = gnn_model.train(df)
            gnn_model.save(test_models_dir)
            
            results['gnn'] = {
                'status': 'success',
                'accuracy': gnn_metrics['accuracy'],
                'roc_auc': gnn_metrics['roc_auc'],
                'num_nodes': gnn_metrics.get('num_nodes', 0),
                'num_edges': gnn_metrics.get('num_edges', 0)
            }
            logger.info(f"✅ GNN: Accuracy={gnn_metrics['accuracy']:.4f}, AUC={gnn_metrics['roc_auc']:.4f}")
            logger.info(f"   Graph: {gnn_metrics.get('num_nodes', 0)} nodes, {gnn_metrics.get('num_edges', 0)} edges")
            
        except Exception as e:
            logger.error(f"❌ GNN failed: {e}")
            results['gnn'] = {'status': 'failed', 'error': str(e)}
    else:
        results['gnn'] = {'status': 'unavailable', 'reason': 'Missing torch-geometric'}
        logger.info("⚠️ GNN unavailable (missing torch-geometric)")
    
    # Test 4: Ensemble loading
    logger.info("\n🎭 Testing Ensemble Loading...")
    try:
        from src.models import EdgeOptimizedModel
        
        ensemble = EdgeOptimizedModel(test_models_dir)
        ensemble.load_models()
        
        # Test ensemble prediction
        test_features = {
            'url_length': 25.0,
            'url_entropy': 3.5,
            'domain_length': 12.0,
            'has_https': 1.0,
            'url': 'https://example.com/test'
        }
        
        prediction = ensemble.predict_single(test_features)
        logger.info(f"✅ Ensemble prediction: {prediction}")
        
        results['ensemble'] = {
            'status': 'success',
            'prediction': prediction
        }
        
    except Exception as e:
        logger.error(f"❌ Ensemble failed: {e}")
        results['ensemble'] = {'status': 'failed', 'error': str(e)}
    
    # Generate test report
    report_file = test_reports_dir / "multi_model_test_results.txt"
    with open(report_file, 'w') as f:
        f.write("Multi-Model Training Test Results\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Test Dataset: {len(df)} samples\n")
        f.write(f"Label distribution: {dict(df['label'].value_counts())}\n\n")
        
        for model_name, result in results.items():
            f.write(f"{model_name.upper()} Results:\n")
            f.write(f"  Status: {result['status']}\n")
            
            if result['status'] == 'success':
                if 'accuracy' in result:
                    f.write(f"  Accuracy: {result['accuracy']:.4f}\n")
                if 'roc_auc' in result:
                    f.write(f"  ROC-AUC: {result['roc_auc']:.4f}\n")
                if 'num_nodes' in result:
                    f.write(f"  Graph nodes: {result['num_nodes']}\n")
                if 'num_edges' in result:
                    f.write(f"  Graph edges: {result['num_edges']}\n")
                if 'prediction' in result:
                    f.write(f"  Sample prediction: {result['prediction']}\n")
            elif result['status'] == 'failed':
                f.write(f"  Error: {result.get('error', 'Unknown')}\n")
            elif result['status'] == 'unavailable':
                f.write(f"  Reason: {result.get('reason', 'Unknown')}\n")
            
            f.write("\n")
        
        # Summary
        successful_models = [name for name, result in results.items() if result['status'] == 'success']
        f.write(f"Summary:\n")
        f.write(f"  Successfully trained: {len(successful_models)} models\n")
        f.write(f"  Models: {', '.join(successful_models)}\n")
    
    logger.info(f"\n📊 Test results saved to: {report_file}")
    logger.info(f"🎉 Multi-model test completed!")
    logger.info(f"✅ Successfully trained: {len([r for r in results.values() if r['status'] == 'success'])} models")
    
    return len([r for r in results.values() if r['status'] == 'success']) > 0

if __name__ == "__main__":
    success = test_multi_model_training()
    sys.exit(0 if success else 1)