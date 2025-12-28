#!/usr/bin/env python3
"""
Feature Importance Analysis for Edge-AI URL Detection
Comprehensive feature analysis and ablation study
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, f1_score
import joblib
import json
import os

class FeatureImportanceAnalysis:
    def __init__(self, data_path, model_path=None):
        """Initialize feature importance analysis"""
        self.data_path = data_path
        self.model_path = model_path
        self.model = None
        self.feature_names = []
        self.feature_categories = {}
        
    def load_model_and_data(self):
        """Load trained model and test data"""
        print("Loading model and data...")
        
        # Load trained Random Forest model
        if self.model_path and os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            # Train a new model if not available
            print("Training new Random Forest model...")
            self.train_new_model()
        
        # Load features dataset directly
        self.test_features = pd.read_csv(os.path.join(self.data_path, 'processed/test_features.csv'))
        
        # Prepare feature columns
        self.feature_names = [col for col in self.test_features.columns if col not in ['label', 'source']]
        self.X_test = self.test_features[self.feature_names].fillna(0)
        self.y_test = self.test_features['label']
        
        # Define feature categories
        self.define_feature_categories()
        
        print(f"Features loaded: {len(self.feature_names)}")
        print(f"Test samples: {len(self.X_test)}")
    
    def train_new_model(self):
        """Train new Random Forest model if needed"""
        # Load training data
        train_features = pd.read_csv(os.path.join(self.data_path, 'processed/train_features.csv'))
        feature_cols = [col for col in train_features.columns if col not in ['label', 'source']]
        
        X_train = train_features[feature_cols].fillna(0)
        y_train = train_features['label']
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        print("Model training completed")
    
    def define_feature_categories(self):
        """Define feature categories for analysis"""
        self.feature_categories = {
            'URL_Lexical': [
                'url_length', 'domain_length', 'path_length', 'query_length',
                'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes',
                'num_digits', 'num_special_chars', 'has_ip_address', 
                'suspicious_keywords', 'url_entropy'
            ],
            'Domain_Analysis': [
                'domain_age_days', 'domain_reputation_score', 'subdomain_count',
                'domain_in_title', 'domain_tokens', 'tld_legitimacy'
            ],
            'SSL_Security': [
                'ssl_valid', 'ssl_issuer_trusted', 'ssl_self_signed', 
                'ssl_expired', 'certificate_age_days'
            ],
            'DNS_Network': [
                'dns_response_time', 'dns_record_count', 'mx_record_exists',
                'ns_record_count', 'geo_location_risk'
            ],
            'Content_Metadata': [
                'page_rank_score', 'redirect_count', 'external_links_count',
                'forms_count', 'iframes_count'
            ]
        }
        
        # Verify feature names exist in dataset
        available_features = set(self.feature_names)
        for category, features in self.feature_categories.items():
            self.feature_categories[category] = [f for f in features if f in available_features]
    
    def calculate_feature_importance(self):
        """Calculate multiple types of feature importance"""
        print("Calculating feature importance...")
        
        results = {}
        
        # 1. Random Forest built-in importance (Gini impurity)
        if hasattr(self.model, 'feature_importances_'):
            rf_importance = self.model.feature_importances_
            results['gini_importance'] = dict(zip(self.feature_names, rf_importance))
        
        # 2. Permutation importance (more robust)
        print("Computing permutation importance...")
        perm_importance = permutation_importance(
            self.model, self.X_test, self.y_test, 
            n_repeats=5, random_state=42, n_jobs=-1
        )
        results['permutation_importance'] = dict(zip(self.feature_names, perm_importance.importances_mean))
        results['permutation_std'] = dict(zip(self.feature_names, perm_importance.importances_std))
        
        return results
    
    def run_ablation_study(self):
        """Run ablation study by feature categories"""
        print("Running ablation study...")
        
        # Baseline performance
        baseline_pred = self.model.predict(self.X_test)
        baseline_accuracy = accuracy_score(self.y_test, baseline_pred)
        baseline_f1 = f1_score(self.y_test, baseline_pred, average='weighted')
        
        ablation_results = {
            'baseline': {
                'accuracy': baseline_accuracy,
                'f1_score': baseline_f1,
                'features_used': len(self.feature_names)
            }
        }
        
        # Test performance when removing each category
        for category_name, category_features in self.feature_categories.items():
            if not category_features:
                continue
                
            print(f"Testing without {category_name} features...")
            
            # Create feature set without this category
            remaining_features = [f for f in self.feature_names if f not in category_features]
            
            if len(remaining_features) == 0:
                continue
                
            # Get indices of remaining features
            remaining_indices = [self.feature_names.index(f) for f in remaining_features]
            X_ablation = self.X_test.iloc[:, remaining_indices]
            
            # Predict with reduced feature set
            pred_ablation = self.model.predict(X_ablation)
            
            accuracy_ablation = accuracy_score(self.y_test, pred_ablation)
            f1_ablation = f1_score(self.y_test, pred_ablation, average='weighted')
            
            # Calculate performance drop
            accuracy_drop = baseline_accuracy - accuracy_ablation
            f1_drop = baseline_f1 - f1_ablation
            
            ablation_results[f'without_{category_name}'] = {
                'accuracy': accuracy_ablation,
                'f1_score': f1_ablation,
                'accuracy_drop': accuracy_drop,
                'f1_drop': f1_drop,
                'features_removed': len(category_features),
                'features_used': len(remaining_features)
            }
        
        return ablation_results
    
    def generate_visualizations(self, importance_results, ablation_results, output_dir):
        """Generate feature importance visualizations"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Top 15 Most Important Features (Permutation)
        perm_imp = importance_results['permutation_importance']
        top_features = sorted(perm_imp.items(), key=lambda x: x[1], reverse=True)[:15]
        
        plt.figure(figsize=(12, 8))
        features, importances = zip(*top_features)
        y_pos = np.arange(len(features))
        
        plt.barh(y_pos, importances, color='skyblue', edgecolor='navy', alpha=0.7)
        plt.yticks(y_pos, features)
        plt.xlabel('Permutation Importance')
        plt.title('Top 15 Most Important Features for URL Detection')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'top_15_features.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Feature Importance by Category
        category_importance = {}
        for category, features in self.feature_categories.items():
            if features:
                avg_importance = np.mean([perm_imp.get(f, 0) for f in features])
                category_importance[category] = avg_importance
        
        plt.figure(figsize=(10, 6))
        categories = list(category_importance.keys())
        importances = list(category_importance.values())
        
        bars = plt.bar(categories, importances, color='lightcoral', edgecolor='darkred', alpha=0.7)
        plt.xlabel('Feature Categories')
        plt.ylabel('Average Permutation Importance')
        plt.title('Feature Importance by Category')
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                    f'{height:.3f}', ha='center', va='bottom')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'category_importance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Ablation Study Results
        categories = []
        accuracy_drops = []
        f1_drops = []
        
        for key, results in ablation_results.items():
            if key.startswith('without_'):
                category = key.replace('without_', '').replace('_', ' ')
                categories.append(category)
                accuracy_drops.append(results['accuracy_drop'] * 100)
                f1_drops.append(results['f1_drop'] * 100)
        
        x = np.arange(len(categories))
        width = 0.35
        
        plt.figure(figsize=(12, 6))
        bars1 = plt.bar(x - width/2, accuracy_drops, width, label='Accuracy Drop', color='lightblue', alpha=0.7)
        bars2 = plt.bar(x + width/2, f1_drops, width, label='F1-Score Drop', color='lightgreen', alpha=0.7)
        
        plt.xlabel('Feature Category Removed')
        plt.ylabel('Performance Drop (%)')
        plt.title('Ablation Study: Impact of Removing Feature Categories')
        plt.xticks(x, categories, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.2f}%', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'ablation_study.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {output_dir}")
    
    def save_results(self, importance_results, ablation_results, output_dir):
        """Save all feature analysis results"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save feature importance
        with open(os.path.join(output_dir, 'feature_importance.json'), 'w') as f:
            json.dump(importance_results, f, indent=2)
        
        # Save ablation results
        with open(os.path.join(output_dir, 'ablation_study.json'), 'w') as f:
            json.dump(ablation_results, f, indent=2)
        
        # Create feature importance table for paper
        perm_imp = importance_results['permutation_importance']
        perm_std = importance_results['permutation_std']
        
        feature_table = []
        for feature in sorted(perm_imp.keys(), key=lambda x: perm_imp[x], reverse=True):
            # Find category
            category = 'Other'
            for cat, features in self.feature_categories.items():
                if feature in features:
                    category = cat.replace('_', ' ')
                    break
            
            feature_table.append({
                'Feature': feature.replace('_', ' ').title(),
                'Category': category,
                'Importance': f"{perm_imp[feature]:.4f}",
                'Std Dev': f"{perm_std[feature]:.4f}"
            })
        
        feature_df = pd.DataFrame(feature_table)
        feature_df.to_csv(os.path.join(output_dir, 'feature_importance_table.csv'), index=False)
        
        # Generate LaTeX table for top features
        top_15_df = feature_df.head(15)
        latex_table = top_15_df.to_latex(index=False, escape=False)
        with open(os.path.join(output_dir, 'top_features_table.tex'), 'w') as f:
            f.write(latex_table)
        
        print(f"Feature analysis results saved to {output_dir}")
        return feature_df

def main():
    """Main execution function"""
    
    data_path = '/home/dtu/project_URL/Edge-AI-URL-Detection/data'
    model_path = '/home/dtu/project_URL/Edge-AI-URL-Detection/models/rf_model.joblib'
    output_dir = '/home/dtu/project_URL/Edge-AI-URL-Detection/reports/feature_analysis'
    
    # Initialize analysis
    analyzer = FeatureImportanceAnalysis(data_path, model_path)
    
    # Load model and data
    analyzer.load_model_and_data()
    
    # Calculate feature importance
    importance_results = analyzer.calculate_feature_importance()
    
    # Run ablation study
    ablation_results = analyzer.run_ablation_study()
    
    # Generate visualizations
    analyzer.generate_visualizations(importance_results, ablation_results, output_dir)
    
    # Save results
    feature_df = analyzer.save_results(importance_results, ablation_results, output_dir)
    
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
    print("="*60)
    print(f"Results available in: {output_dir}")
    print("\nTop 10 Most Important Features:")
    print(feature_df.head(10).to_string(index=False))

if __name__ == "__main__":
    main()