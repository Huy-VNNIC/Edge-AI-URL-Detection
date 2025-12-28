#!/usr/bin/env python3
"""
Comprehensive Model Comparison for Edge-AI URL Detection
Comparing Random Forest with other AI models for academic rigor
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import time
import psutil
import os
import joblib
import json

class ModelComparison:
    def __init__(self, data_path):
        """Initialize model comparison with dataset"""
        self.data_path = data_path
        self.models = {}
        self.results = {}
        
    def load_data(self):
        """Load preprocessed training and test data"""
        print("Loading dataset...")
        
        # Load processed features directly 
        train_features = pd.read_csv(os.path.join(self.data_path, 'processed/train_features.csv'))
        test_features = pd.read_csv(os.path.join(self.data_path, 'processed/test_features.csv'))
        
        # Prepare feature columns (exclude label and source)
        feature_cols = [col for col in train_features.columns if col not in ['label', 'source']]
        
        self.X_train = train_features[feature_cols].fillna(0)
        self.y_train = train_features['label']
        self.X_test = test_features[feature_cols].fillna(0)
        self.y_test = test_features['label']
        
        print(f"Training samples: {len(self.X_train)}")
        print(f"Test samples: {len(self.X_test)}")
        print(f"Features: {len(feature_cols)}")
        
    def initialize_models(self):
        """Initialize all models for comparison"""
        print("Initializing models...")
        
        self.models = {
            'Random_Forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10, 
                random_state=42,
                n_jobs=-1
            ),
            'Logistic_Regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            ),
            'SVM': SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            ),
            'XGBoost': XGBClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42,
                n_jobs=-1,
                eval_metric='logloss'
            ),
            'Neural_Network': MLPClassifier(
                hidden_layer_sizes=(64, 32),
                max_iter=500,
                random_state=42
            )
        }
        
    def measure_memory_usage(self):
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def train_and_evaluate_model(self, name, model):
        """Train and evaluate a single model"""
        print(f"\nTraining {name}...")
        
        # Measure memory before training
        memory_before = self.measure_memory_usage()
        
        # Training time
        start_time = time.time()
        model.fit(self.X_train, self.y_train)
        training_time = time.time() - start_time
        
        # Memory after training
        memory_after = self.measure_memory_usage()
        model_memory = memory_after - memory_before
        
        # Prediction time (batch)
        start_time = time.time()
        y_pred = model.predict(self.X_test)
        batch_inference_time = time.time() - start_time
        
        # Single sample inference time (average of 100 samples)
        single_times = []
        for i in range(min(100, len(self.X_test))):
            start_time = time.time()
            _ = model.predict(self.X_test.iloc[[i]])
            single_times.append((time.time() - start_time) * 1000)  # Convert to ms
        
        avg_single_inference = np.mean(single_times)
        
        # Calculate metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, average='weighted')
        recall = recall_score(self.y_test, y_pred, average='weighted')
        f1 = f1_score(self.y_test, y_pred, average='weighted')
        
        # Model size (approximate)
        model_size_mb = 0
        try:
            # Try to save and measure model size
            temp_path = f'/tmp/{name}_temp_model.joblib'
            joblib.dump(model, temp_path)
            model_size_mb = os.path.getsize(temp_path) / 1024 / 1024
            os.remove(temp_path)
        except:
            model_size_mb = model_memory  # Fallback to memory usage
        
        return {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_time_sec': training_time,
            'avg_inference_time_ms': avg_single_inference,
            'batch_inference_time_sec': batch_inference_time,
            'model_size_mb': model_size_mb,
            'memory_usage_mb': model_memory,
            'throughput_samples_per_sec': len(self.X_test) / batch_inference_time
        }
    
    def run_comparison(self):
        """Run comprehensive model comparison"""
        print("Starting comprehensive model comparison...")
        
        self.load_data()
        self.initialize_models()
        
        # Train and evaluate each model
        for name, model in self.models.items():
            try:
                self.results[name] = self.train_and_evaluate_model(name, model)
                print(f"✅ {name} completed successfully")
            except Exception as e:
                print(f"❌ {name} failed: {str(e)}")
                continue
    
    def generate_comparison_table(self):
        """Generate comparison table for paper"""
        
        # Create comparison DataFrame
        comparison_data = []
        
        for model_name, results in self.results.items():
            comparison_data.append({
                'Model': model_name.replace('_', ' '),
                'Accuracy (%)': f"{results['accuracy']*100:.2f}",
                'F1-Score': f"{results['f1_score']:.4f}",
                'Inference Time (ms)': f"{results['avg_inference_time_ms']:.2f}",
                'Model Size (MB)': f"{results['model_size_mb']:.2f}",
                'Memory Usage (MB)': f"{results['memory_usage_mb']:.2f}",
                'Throughput (samples/sec)': f"{results['throughput_samples_per_sec']:.1f}"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Sort by accuracy descending
        comparison_df = comparison_df.sort_values('Accuracy (%)', ascending=False)
        
        return comparison_df
    
    def save_results(self, output_dir):
        """Save all results for paper"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results
        with open(os.path.join(output_dir, 'model_comparison_detailed.json'), 'w') as f:
            # Convert numpy types to native Python for JSON serialization
            serializable_results = {}
            for model_name, results in self.results.items():
                serializable_results[model_name] = {}
                for key, value in results.items():
                    if key == 'model':
                        continue  # Skip model objects
                    elif isinstance(value, (np.integer, np.floating)):
                        serializable_results[model_name][key] = value.item()
                    else:
                        serializable_results[model_name][key] = value
            
            json.dump(serializable_results, f, indent=2)
        
        # Save comparison table
        comparison_df = self.generate_comparison_table()
        comparison_df.to_csv(os.path.join(output_dir, 'model_comparison_table.csv'), index=False)
        
        # Generate LaTeX table
        latex_table = comparison_df.to_latex(index=False, escape=False)
        with open(os.path.join(output_dir, 'model_comparison_table.tex'), 'w') as f:
            f.write(latex_table)
        
        print(f"Results saved to {output_dir}")
        print("\nComparison Table:")
        print(comparison_df.to_string(index=False))
        
        return comparison_df

def main():
    """Main execution function"""
    
    # Initialize comparison
    data_path = '/home/dtu/project_URL/Edge-AI-URL-Detection/data'
    output_dir = '/home/dtu/project_URL/Edge-AI-URL-Detection/reports/model_comparison'
    
    comparator = ModelComparison(data_path)
    
    # Run comparison
    comparator.run_comparison()
    
    # Save results
    results_df = comparator.save_results(output_dir)
    
    print("\n" + "="*60)
    print("MODEL COMPARISON COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"Results available in: {output_dir}")
    print("Files generated:")
    print("- model_comparison_detailed.json")
    print("- model_comparison_table.csv") 
    print("- model_comparison_table.tex")

if __name__ == "__main__":
    main()