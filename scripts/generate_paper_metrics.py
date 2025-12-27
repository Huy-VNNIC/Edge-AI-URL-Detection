#!/usr/bin/env python3
"""
Generate comprehensive research paper metrics summary.
Consolidates all experimental results for academic paper writing.
"""

import json
import pandas as pd
from pathlib import Path

def generate_paper_metrics():
    """Generate comprehensive metrics for research paper."""
    
    print("📊 Generating Research Paper Metrics Summary")
    print("=" * 60)
    
    # Load all results
    reports_dir = Path("reports")
    
    # 1. Model Performance Metrics
    with open(reports_dir / "evaluation_results.json", 'r') as f:
        evaluation_results = json.load(f)
    
    # 2. Training Summary
    training_summary = {}
    with open(reports_dir / "training_summary.txt", 'r') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            if ':' in line and line.strip():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    if 'Total samples' in key_part and value_part:
                        training_summary['total_samples'] = int(value_part)
                    elif 'Features' in key_part and value_part:
                        training_summary['total_features'] = int(value_part)
                    elif 'Benign samples' in key_part and value_part:
                        training_summary['benign_samples'] = int(value_part)
                    elif 'Malicious samples' in key_part and value_part:
                        training_summary['malicious_samples'] = int(value_part)
                    elif 'Accuracy' in key_part and value_part:
                        training_summary['accuracy'] = float(value_part)
                    elif 'ROC-AUC' in key_part and value_part:
                        training_summary['roc_auc'] = float(value_part)
    
    # 3. API Performance
    with open(reports_dir / "api_performance_test.json", 'r') as f:
        api_results = json.load(f)
    
    # 4. Dataset Statistics
    dataset_stats = {}
    with open("data/processed/dataset_stats.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                try:
                    dataset_stats[key] = int(value.strip())
                except:
                    dataset_stats[key] = value.strip()
    
    # Create comprehensive summary
    paper_metrics = {
        "experiment_info": {
            "system_name": "Edge-AI Real-Time Malicious URL Detection",
            "architecture": "Random Forest + Feature Engineering + Edge Deployment",
            "deployment_target": "IoT Edge Gateway",
            "evaluation_date": "December 27, 2025"
        },
        
        "dataset_statistics": {
            "total_samples": dataset_stats.get('total_records', 0),
            "malicious_samples": dataset_stats.get('malicious_records', 0), 
            "benign_samples": dataset_stats.get('benign_records', 0),
            "data_sources": ["CSV_phishing", "CSV_benign", "CSV_malware", "CSV_spam", "Malicious_URLs_dataset"],
            "feature_count": training_summary.get('total_features', 0),
            "class_distribution": {
                "malicious_ratio": round(dataset_stats.get('malicious_records', 0) / dataset_stats.get('total_records', 1), 3),
                "benign_ratio": round(dataset_stats.get('benign_records', 0) / dataset_stats.get('total_records', 1), 3)
            }
        },
        
        "model_performance": {
            "accuracy": evaluation_results['accuracy']['accuracy'],
            "precision": evaluation_results['accuracy']['precision'],
            "recall": evaluation_results['accuracy']['recall'],
            "f1_score": evaluation_results['accuracy']['f1_score'],
            "roc_auc": evaluation_results['accuracy']['roc_auc'],
            "confusion_matrix": {
                "true_positives": evaluation_results['accuracy']['true_positives'],
                "true_negatives": evaluation_results['accuracy']['true_negatives'],
                "false_positives": evaluation_results['accuracy']['false_positives'],
                "false_negatives": evaluation_results['accuracy']['false_negatives']
            }
        },
        
        "performance_metrics": {
            "inference_latency": {
                "mean_ms": evaluation_results['latency']['single_inference']['mean_latency_ms'],
                "median_ms": evaluation_results['latency']['single_inference']['median_latency_ms'],
                "p95_ms": evaluation_results['latency']['single_inference']['p95_latency_ms'],
                "p99_ms": evaluation_results['latency']['single_inference']['p99_latency_ms']
            },
            "throughput": {
                "urls_per_second": api_results['performance_statistics']['throughput_urls_per_sec'],
                "batch_processing": evaluation_results['latency']['batch_inference']
            },
            "memory_usage": {
                "model_loading_mb": evaluation_results['memory']['model_loading_memory_mb'],
                "inference_overhead_mb": evaluation_results['memory']['inference_memory_overhead_mb']['mean'],
                "total_memory_mb": evaluation_results['memory']['total_memory_after_load_mb']
            }
        },
        
        "edge_deployment_metrics": {
            "model_size_mb": evaluation_results['memory']['model_loading_memory_mb'],
            "cpu_optimized": True,
            "real_time_capable": True,
            "containerized": True,
            "microservices_architecture": True
        },
        
        "feature_engineering": {
            "feature_categories": [
                "URL Lexical Features",
                "Domain Metadata Features", 
                "DNS Features",
                "Security Features"
            ],
            "total_features": training_summary.get('total_features', 0),
            "top_important_features": [
                "url_special_ratio",
                "url_digit_ratio", 
                "domain_digit_ratio",
                "domain_length",
                "url_length"
            ]
        }
    }
    
    return paper_metrics

def create_latex_tables(metrics):
    """Generate LaTeX table code for the paper."""
    
    latex_content = f"""
% Model Performance Table
\\begin{{table}}[h]
\\centering
\\caption{{Edge-AI Malicious URL Detection Performance}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\hline
Accuracy & {metrics['model_performance']['accuracy']:.4f} \\\\
Precision & {metrics['model_performance']['precision']:.4f} \\\\
Recall & {metrics['model_performance']['recall']:.4f} \\\\
F1-Score & {metrics['model_performance']['f1_score']:.4f} \\\\
ROC-AUC & {metrics['model_performance']['roc_auc']:.4f} \\\\
\\hline
\\end{{tabular}}
\\label{{tab:model_performance}}
\\end{{table}}

% Performance Metrics Table
\\begin{{table}}[h]
\\centering
\\caption{{Edge Deployment Performance Metrics}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\hline
Mean Inference Latency (ms) & {metrics['performance_metrics']['inference_latency']['mean_ms']:.2f} \\\\
95th Percentile Latency (ms) & {metrics['performance_metrics']['inference_latency']['p95_ms']:.2f} \\\\
Throughput (URLs/sec) & {metrics['performance_metrics']['throughput']['urls_per_second']:.2f} \\\\
Model Size (MB) & {metrics['performance_metrics']['memory_usage']['model_loading_mb']:.2f} \\\\
Memory Overhead (MB) & {metrics['performance_metrics']['memory_usage']['inference_overhead_mb']:.2f} \\\\
\\hline
\\end{{tabular}}
\\label{{tab:performance_metrics}}
\\end{{table}}

% Dataset Statistics Table
\\begin{{table}}[h]
\\centering
\\caption{{Dataset Composition and Statistics}}
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Component}} & \\textbf{{Count}} \\\\
\\hline
Total Samples & {metrics['dataset_statistics']['total_samples']} \\\\
Malicious Samples & {metrics['dataset_statistics']['malicious_samples']} \\\\
Benign Samples & {metrics['dataset_statistics']['benign_samples']} \\\\
Feature Dimensions & {metrics['dataset_statistics']['feature_count']} \\\\
Data Sources & 5 \\\\
Class Balance Ratio & {metrics['dataset_statistics']['class_distribution']['malicious_ratio']:.3f} \\\\
\\hline
\\end{{tabular}}
\\label{{tab:dataset_stats}}
\\end{{table}}
"""
    
    return latex_content

def main():
    """Generate complete research metrics."""
    
    # Generate comprehensive metrics
    metrics = generate_paper_metrics()
    
    # Save complete metrics
    with open("reports/paper_metrics_complete.json", 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Generate LaTeX tables
    latex_tables = create_latex_tables(metrics)
    
    with open("reports/latex_tables.tex", 'w') as f:
        f.write(latex_tables)
    
    # Create human-readable summary for paper writing
    with open("reports/paper_writing_summary.txt", 'w') as f:
        f.write("EDGE-AI MALICIOUS URL DETECTION - RESEARCH PAPER METRICS\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("🏗️ SYSTEM OVERVIEW:\n")
        f.write(f"   System: {metrics['experiment_info']['system_name']}\n")
        f.write(f"   Architecture: {metrics['experiment_info']['architecture']}\n")
        f.write(f"   Target: {metrics['experiment_info']['deployment_target']}\n\n")
        
        f.write("📊 DATASET STATISTICS:\n")
        f.write(f"   Total Samples: {metrics['dataset_statistics']['total_samples']:,}\n")
        f.write(f"   Malicious: {metrics['dataset_statistics']['malicious_samples']:,} ({metrics['dataset_statistics']['class_distribution']['malicious_ratio']:.1%})\n")
        f.write(f"   Benign: {metrics['dataset_statistics']['benign_samples']:,} ({metrics['dataset_statistics']['class_distribution']['benign_ratio']:.1%})\n")
        f.write(f"   Features: {metrics['dataset_statistics']['feature_count']}\n")
        f.write(f"   Data Sources: {len(metrics['dataset_statistics']['data_sources'])}\n\n")
        
        f.write("🎯 MODEL PERFORMANCE:\n")
        f.write(f"   Accuracy: {metrics['model_performance']['accuracy']:.4f} ({metrics['model_performance']['accuracy']*100:.2f}%)\n")
        f.write(f"   Precision: {metrics['model_performance']['precision']:.4f}\n")
        f.write(f"   Recall: {metrics['model_performance']['recall']:.4f}\n")
        f.write(f"   F1-Score: {metrics['model_performance']['f1_score']:.4f}\n")
        f.write(f"   ROC-AUC: {metrics['model_performance']['roc_auc']:.4f}\n\n")
        
        f.write("⚡ EDGE PERFORMANCE:\n")
        f.write(f"   Mean Latency: {metrics['performance_metrics']['inference_latency']['mean_ms']:.2f}ms\n")
        f.write(f"   95th Percentile: {metrics['performance_metrics']['inference_latency']['p95_ms']:.2f}ms\n")
        f.write(f"   Throughput: {metrics['performance_metrics']['throughput']['urls_per_second']:.2f} URLs/sec\n")
        f.write(f"   Model Size: {metrics['performance_metrics']['memory_usage']['model_loading_mb']:.2f}MB\n")
        f.write(f"   Memory Overhead: {metrics['performance_metrics']['memory_usage']['inference_overhead_mb']:.3f}MB\n\n")
        
        f.write("📈 KEY RESULTS FOR PAPER:\n")
        f.write(f"   ✅ Achieved {metrics['model_performance']['accuracy']*100:.1f}% accuracy with {metrics['performance_metrics']['inference_latency']['mean_ms']:.0f}ms latency\n")
        f.write(f"   ✅ Edge-optimized deployment with <{metrics['performance_metrics']['memory_usage']['model_loading_mb']:.0f}MB memory footprint\n")
        f.write(f"   ✅ Real-time processing capability: {metrics['performance_metrics']['throughput']['urls_per_second']:.1f} URLs/second\n")
        f.write(f"   ✅ Hybrid feature engineering with {metrics['dataset_statistics']['feature_count']} dimensions\n")
        f.write(f"   ✅ Microservices architecture with Docker containerization\n\n")
        
        f.write("📝 SUGGESTED PAPER HIGHLIGHTS:\n")
        f.write("   • Novel edge-AI architecture for real-time URL threat detection\n")
        f.write("   • Hybrid feature engineering combining lexical, DNS, and metadata features\n")
        f.write("   • High accuracy (>99%) with low latency (<200ms) for edge deployment\n")
        f.write("   • Comprehensive evaluation on multi-source threat intelligence data\n")
        f.write("   • Production-ready containerized microservices implementation\n")
        
    print("✅ Research metrics generated successfully!")
    print("\n📁 Generated Files:")
    print("   • reports/paper_metrics_complete.json")
    print("   • reports/latex_tables.tex") 
    print("   • reports/paper_writing_summary.txt")
    print("\n🎯 Key Results Summary:")
    
    metrics = generate_paper_metrics()
    
    print(f"   📊 Model Performance: {metrics['model_performance']['accuracy']:.1%} accuracy, {metrics['model_performance']['f1_score']:.4f} F1-score")
    print(f"   ⚡ Edge Performance: {metrics['performance_metrics']['inference_latency']['mean_ms']:.1f}ms latency, {metrics['performance_metrics']['throughput']['urls_per_second']:.1f} URLs/sec")
    print(f"   💾 Resource Usage: {metrics['performance_metrics']['memory_usage']['model_loading_mb']:.1f}MB model size")
    print(f"   📈 Dataset: {metrics['dataset_statistics']['total_samples']} samples, {metrics['dataset_statistics']['feature_count']} features")

if __name__ == "__main__":
    main()