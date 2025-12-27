"""Machine learning models for malicious URL/domain detection."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import joblib
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils import setup_logging, load_config

logger = setup_logging()

# Import additional models
try:
    from .transformer import TransformerModel
    TRANSFORMER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Transformer model not available: {e}")
    TransformerModel = None
    TRANSFORMER_AVAILABLE = False

try:
    from .gnn import GNNModel
    GNN_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GNN model not available: {e}")
    GNNModel = None
    GNN_AVAILABLE = False

class RandomForestModel:
    """Random Forest model for tabular feature classification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config['models']['random_forest']
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: list) -> Dict[str, Any]:
        """Train Random Forest model."""
        logger.info("Training Random Forest model...")
        
        self.feature_names = feature_names
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=self.config['n_estimators'],
            max_depth=self.config.get('max_depth'),
            min_samples_split=self.config['min_samples_split'],
            class_weight=self.config['class_weight'],
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_prob = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'feature_importance': dict(zip(feature_names, self.model.feature_importances_))
        }
        
        logger.info(f"Random Forest Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Random Forest ROC-AUC: {metrics['roc_auc']:.4f}")
        
        return metrics
        
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained yet")
            
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return predictions, probabilities
        
    def save(self, model_dir: Path):
        """Save model and scaler."""
        model_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, model_dir / 'rf_model.joblib')
        joblib.dump(self.scaler, model_dir / 'rf_scaler.joblib')
        
        # Save feature names
        with open(model_dir / 'rf_features.txt', 'w') as f:
            for feature in self.feature_names:
                f.write(f"{feature}\n")
                
        logger.info(f"Random Forest model saved to {model_dir}")
        
    def load(self, model_dir: Path):
        """Load model and scaler."""
        self.model = joblib.load(model_dir / 'rf_model.joblib')
        self.scaler = joblib.load(model_dir / 'rf_scaler.joblib')
        
        # Load feature names
        with open(model_dir / 'rf_features.txt', 'r') as f:
            self.feature_names = [line.strip() for line in f]
            
        logger.info(f"Random Forest model loaded from {model_dir}")

class ModelEvaluator:
    """Evaluate and compare different models."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, 
                            model_name: str, save_path: Optional[Path] = None):
        """Plot and save confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Benign', 'Malicious'],
                   yticklabels=['Benign', 'Malicious'])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        
        if save_path is None:
            save_path = self.output_dir / f'{model_name.lower()}_confusion_matrix.png'
            
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved confusion matrix to {save_path}")
        
    def plot_feature_importance(self, feature_importance: Dict[str, float], 
                              model_name: str, top_n: int = 20):
        """Plot feature importance."""
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), 
                               key=lambda x: x[1], reverse=True)[:top_n]
        
        features, importances = zip(*sorted_features)
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(features)), importances)
        plt.yticks(range(len(features)), features)
        plt.xlabel('Feature Importance')
        plt.title(f'Top {top_n} Feature Importance - {model_name}')
        plt.gca().invert_yaxis()
        
        save_path = self.output_dir / f'{model_name.lower()}_feature_importance.png'
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved feature importance plot to {save_path}")
        
    def save_metrics_report(self, metrics: Dict[str, Any], model_name: str):
        """Save detailed metrics report."""
        report_path = self.output_dir / f'{model_name.lower()}_metrics.txt'
        
        with open(report_path, 'w') as f:
            f.write(f"Evaluation Report - {model_name}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Accuracy: {metrics['accuracy']:.4f}\n")
            f.write(f"ROC-AUC: {metrics['roc_auc']:.4f}\n\n")
            
            f.write("Classification Report:\n")
            f.write("-" * 30 + "\n")
            
            clf_report = metrics['classification_report']
            for label, metrics_dict in clf_report.items():
                if isinstance(metrics_dict, dict):
                    f.write(f"\n{label}:\n")
                    for metric, value in metrics_dict.items():
                        f.write(f"  {metric}: {value:.4f}\n")
                        
        logger.info(f"Saved metrics report to {report_path}")

class EdgeOptimizedModel:
    """Wrapper for edge-optimized inference with ensemble models."""
    
    def __init__(self, models_dir: Path):
        self.models_dir = models_dir
        self.rf_model = None
        self.transformer_model = None
        self.gnn_model = None
        
    def load_models(self):
        """Load all trained models for ensemble inference."""
        # Load Random Forest
        self.rf_model = RandomForestModel({'models': {'random_forest': {}}})
        self.rf_model.load(self.models_dir)
        
        # Load Transformer model if available
        if TRANSFORMER_AVAILABLE and (self.models_dir / 'transformer_model.pth').exists():
            try:
                config = {'transformer': {}}
                self.transformer_model = TransformerModel(config)
                self.transformer_model.load(self.models_dir)
                logger.info("Transformer model loaded for ensemble")
            except Exception as e:
                logger.warning(f"Failed to load Transformer model: {e}")
                self.transformer_model = None
        
        # Load GNN model if available  
        if GNN_AVAILABLE and (self.models_dir / 'gnn_model.pth').exists():
            try:
                config = {'gnn': {}}
                self.gnn_model = GNNModel(config)
                self.gnn_model.load(self.models_dir)
                logger.info("GNN model loaded for ensemble")
            except Exception as e:
                logger.warning(f"Failed to load GNN model: {e}")
                self.gnn_model = None
        
        logger.info("Edge-optimized ensemble models loaded")
        
    def predict_single(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict single sample using ensemble (for API)."""
        if self.rf_model is None:
            raise ValueError("Models not loaded")
            
        # Convert features to array in the correct order
        feature_values = []
        for feature_name in self.rf_model.feature_names:
            feature_values.append(features.get(feature_name, 0.0))
            
        feature_array = np.array([feature_values]).reshape(1, -1)
        
        # Get RF prediction (primary model)
        pred, prob = self.rf_model.predict(feature_array)
        
        # Ensemble predictions if other models available
        predictions = [pred[0]]
        probabilities = [prob[0]]
        
        # Add Transformer prediction if available
        if self.transformer_model is not None:
            try:
                # Extract URL from features (if available) or use dummy
                url = features.get('url', 'http://example.com')
                tf_pred, tf_prob = self.transformer_model.predict([url])
                predictions.append(tf_pred[0])
                probabilities.append(tf_prob[0])
            except Exception as e:
                logger.warning(f"Transformer prediction failed: {e}")
        
        # Add GNN prediction if available
        if self.gnn_model is not None:
            try:
                # Create dummy dataframe for GNN
                import pandas as pd
                dummy_df = pd.DataFrame([features])
                gnn_pred, gnn_prob = self.gnn_model.predict(dummy_df)
                predictions.append(gnn_pred[0])
                probabilities.append(gnn_prob[0])
            except Exception as e:
                logger.warning(f"GNN prediction failed: {e}")
        
        # Ensemble decision (majority vote for prediction, average for probability)
        final_prediction = int(np.round(np.mean(predictions)))
        final_probability = float(np.mean(probabilities))
        
        return {
            'prediction': final_prediction,
            'probability': final_probability,
            'label': 'malicious' if final_prediction == 1 else 'benign',
            'confidence': float(max(final_probability, 1 - final_probability)),
            'ensemble_size': len(predictions)
        }
        
    def predict_batch(self, features_batch: np.ndarray) -> Dict[str, Any]:
        """Predict batch of samples (for high throughput)."""
        if self.rf_model is None:
            raise ValueError("Models not loaded")
            
        predictions, probabilities = self.rf_model.predict(features_batch)
        
        return {
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'labels': ['malicious' if p == 1 else 'benign' for p in predictions]
        }