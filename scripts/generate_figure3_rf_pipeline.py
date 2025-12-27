"""
FIGURE 3: Random Forest Edge Inference Pipeline
IEEE/Springer Academic Diagram - Focused on RF Implementation
Avoids overclaiming Transformer/GNN, matches actual performance metrics
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import numpy as np

def create_rf_inference_pipeline():
    """Create Figure 3: Random Forest Edge Inference Pipeline"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Random Forest Edge Inference Pipeline', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Step 1: Input URL
    input_box = FancyBboxPatch((1, 8), 2, 0.6,
                               boxstyle="round,pad=0.1",
                               facecolor='lightblue',
                               edgecolor='black',
                               linewidth=2)
    ax.add_patch(input_box)
    ax.text(2, 8.3, 'Input URL', ha='center', va='center', fontweight='bold', fontsize=11)
    ax.text(2, 7.7, 'https://example.com/path', ha='center', va='center', fontsize=8, style='italic')
    
    # Arrow 1
    ax.arrow(2, 7.7, 0, -0.8, head_width=0.15, head_length=0.1, fc='blue', ec='blue')
    
    # Step 2: Feature Extraction
    feature_box = FancyBboxPatch((0.5, 6), 3, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor='lightgreen',
                                 edgecolor='black',
                                 linewidth=2)
    ax.add_patch(feature_box)
    ax.text(2, 6.8, 'Feature Extraction', ha='center', va='center', fontweight='bold', fontsize=11)
    
    # Feature details
    features_text = """24 Lexical Features:
• URL length, entropy
• Special char ratio
• Domain properties
• Path analysis
3.19ms extraction time"""
    ax.text(2, 6.3, features_text, ha='center', va='center', fontsize=8)
    
    # Arrow 2
    ax.arrow(2, 5.8, 0, -0.8, head_width=0.15, head_length=0.1, fc='blue', ec='blue')
    
    # Step 3: Feature Vector
    vector_box = FancyBboxPatch((1, 4.2), 2, 0.6,
                               boxstyle="round,pad=0.05",
                               facecolor='wheat',
                               edgecolor='black')
    ax.add_patch(vector_box)
    ax.text(2, 4.5, 'Feature Vector', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(2, 4.3, '[x₁, x₂, ..., x₂₄]', ha='center', va='center', fontsize=9, style='italic')
    
    # Arrow 3
    ax.arrow(3.2, 4.5, 1.6, 0, head_width=0.1, head_length=0.15, fc='red', ec='red')
    
    # Step 4: Random Forest Model (MAIN COMPONENT)
    rf_box = FancyBboxPatch((5, 3.5), 3.5, 2,
                           boxstyle="round,pad=0.15",
                           facecolor='orange',
                           edgecolor='black',
                           linewidth=3)
    ax.add_patch(rf_box)
    
    ax.text(6.75, 5.2, 'Random Forest Classifier', ha='center', va='center', 
           fontweight='bold', fontsize=12)
    
    # RF specifications
    rf_specs = """Configuration:
• 100 Decision Trees
• Max Depth: 20
• Min Samples Split: 5
• Balanced Classes

Performance:
• Model Size: 0.26 MB
• Inference: 7.31 ms
• Memory: 6.23 MB total"""
    
    ax.text(6.75, 4.2, rf_specs, ha='center', va='center', fontsize=8)
    
    # Tree visualization (mini trees)
    for i, (x_pos, y_pos) in enumerate([(5.3, 4.8), (6.2, 5.0), (7.1, 4.9), (8.0, 4.7)]):
        if i < 3:
            # Draw mini decision trees
            tree_lines = [
                [(x_pos, y_pos), (x_pos-0.1, y_pos-0.15)],
                [(x_pos, y_pos), (x_pos+0.1, y_pos-0.15)],
                [(x_pos-0.1, y_pos-0.15), (x_pos-0.15, y_pos-0.25)],
                [(x_pos-0.1, y_pos-0.15), (x_pos-0.05, y_pos-0.25)]
            ]
            for line in tree_lines:
                ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]], 'k-', linewidth=1)
        else:
            ax.text(x_pos, y_pos, '...', ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Arrow 4
    ax.arrow(8.7, 4.5, 1.1, 0, head_width=0.1, head_length=0.15, fc='red', ec='red')
    
    # Step 5: Probability Output  
    prob_box = FancyBboxPatch((10, 4), 1.5, 1,
                             boxstyle="round,pad=0.1",
                             facecolor='lightcoral',
                             edgecolor='black')
    ax.add_patch(prob_box)
    ax.text(10.75, 4.7, 'Probability', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(10.75, 4.4, 'P(malicious)', ha='center', va='center', fontsize=9, style='italic')
    ax.text(10.75, 4.1, '[0.0, 1.0]', ha='center', va='center', fontsize=8)
    
    # Arrow 5 (downward)
    ax.arrow(10.75, 3.9, 0, -0.8, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Step 6: Threshold Decision
    threshold_box = FancyBboxPatch((9.5, 2.2), 2.5, 0.8,
                                  boxstyle="round,pad=0.1",
                                  facecolor='yellow',
                                  edgecolor='black',
                                  linewidth=2)
    ax.add_patch(threshold_box)
    ax.text(10.75, 2.7, 'Threshold Decision', ha='center', va='center', fontweight='bold', fontsize=10)
    ax.text(10.75, 2.4, 'If P > 0.5: Malicious', ha='center', va='center', fontsize=8)
    ax.text(10.75, 2.25, 'Else: Benign', ha='center', va='center', fontsize=8)
    
    # Arrow 6 (downward)
    ax.arrow(10.75, 2.1, 0, -0.6, head_width=0.1, head_length=0.1, fc='green', ec='green')
    
    # Step 7: Final Output
    output_box = FancyBboxPatch((9, 0.5), 3.5, 1,
                               boxstyle="round,pad=0.1",
                               facecolor='lightblue',
                               edgecolor='black',
                               linewidth=2)
    ax.add_patch(output_box)
    ax.text(10.75, 1.2, 'Classification Result', ha='center', va='center', fontweight='bold', fontsize=11)
    
    result_text = """Output Format:
{"prediction": 0/1, "probability": 0.836, 
 "label": "benign/malicious", "confidence": 0.836}"""
    ax.text(10.75, 0.8, result_text, ha='center', va='center', fontsize=8)
    
    # Edge Performance Metrics (Left Panel)
    perf_box = FancyBboxPatch((0.2, 0.5), 3.5, 2.8,
                             boxstyle="round,pad=0.1",
                             facecolor='lightyellow',
                             edgecolor='black',
                             linewidth=1)
    ax.add_patch(perf_box)
    
    ax.text(2, 3.1, 'Edge Performance Metrics', ha='center', va='center', 
           fontweight='bold', fontsize=11)
    
    metrics_text = """LATENCY BREAKDOWN:
• Feature Extraction: 3.19 ms (30.4%)
• Model Inference: 7.31 ms (69.6%)
• Total Pipeline: 10.50 ms

THROUGHPUT:
• Offline: 95.3 URLs/sec
• API: 4.9 req/sec (203ms end-to-end)

MEMORY FOOTPRINT:
• Model File: 0.26 MB
• Runtime Total: 6.23 MB
• Edge Compliant: ✓ YES

ACCURACY METRICS:
• Accuracy: 99.31%
• Precision: 99.27%
• Recall: 99.63%
• F1-Score: 99.45%"""
    
    ax.text(2, 2, metrics_text, ha='center', va='center', fontsize=7)
    
    # Edge Deployment Label
    edge_label = FancyBboxPatch((4.5, 0.1), 3, 0.3,
                               boxstyle="round,pad=0.05",
                               facecolor='red',
                               edgecolor='black',
                               alpha=0.8)
    ax.add_patch(edge_label)
    ax.text(6, 0.25, 'OPTIMIZED FOR EDGE DEPLOYMENT', ha='center', va='center', 
           fontweight='bold', fontsize=9, color='white')
    
    # Add timing annotations
    ax.annotate('3.19ms', xy=(2, 5.8), xytext=(4, 6.5),
               arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
               fontsize=9, fontweight='bold', color='red')
    
    ax.annotate('7.31ms', xy=(6.75, 3.4), xytext=(4, 2.5),
               arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
               fontsize=9, fontweight='bold', color='red')
    
    # Add data flow labels
    ax.text(2.5, 5, 'Raw URL', ha='center', va='center', fontsize=8, 
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax.text(4, 4.8, 'Numerical\nFeatures', ha='center', va='center', fontsize=8,
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax.text(9.5, 4.8, 'Model\nOutput', ha='center', va='center', fontsize=8,
           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('reports/Figure3_RF_Inference_Pipeline.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_feature_extraction_detail():
    """Create supplementary figure showing feature extraction details"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(7, 5.5, 'Feature Extraction Pipeline Detail', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    # Input URL
    url_box = FancyBboxPatch((1, 4), 3, 0.8,
                            boxstyle="round,pad=0.1",
                            facecolor='lightblue',
                            edgecolor='black')
    ax.add_patch(url_box)
    ax.text(2.5, 4.4, 'Input URL Example:', ha='center', va='center', fontweight='bold')
    ax.text(2.5, 4.1, 'http://malicious-site.tk/login.php?redirect=evil', 
           ha='center', va='center', fontsize=8, style='italic')
    
    # Feature categories
    categories = [
        ('URL Features', 5.5, 'lightgreen', [
            'url_length: 45',
            'url_entropy: 3.82',
            'url_special_ratio: 0.13',
            'url_digit_ratio: 0.00'
        ]),
        ('Domain Features', 8, 'lightyellow', [
            'domain_length: 16', 
            'domain_entropy: 3.15',
            'suspicious_tld: 1.0',
            'domain_digit_ratio: 0.0'
        ]),
        ('Path Features', 10.5, 'lightcoral', [
            'path_length: 23',
            'num_path_segments: 1',
            'has_suspicious_words: 1.0',
            'path_entropy: 3.42'
        ]),
        ('Query Features', 13, 'wheat', [
            'query_length: 13',
            'num_query_params: 1', 
            'query_entropy: 2.85',
            'has_redirect: 1.0'
        ])
    ]
    
    for cat_name, x_pos, color, features in categories:
        # Category box
        cat_box = FancyBboxPatch((x_pos-1, 2.5), 2, 1.8,
                                boxstyle="round,pad=0.1",
                                facecolor=color,
                                edgecolor='black')
        ax.add_patch(cat_box)
        
        ax.text(x_pos, 4, cat_name, ha='center', va='center', fontweight='bold', fontsize=9)
        
        # Features list
        for i, feature in enumerate(features):
            ax.text(x_pos, 3.6 - i*0.2, feature, ha='center', va='center', fontsize=7)
        
        # Arrow from URL
        ax.arrow(2.5, 3.8, x_pos-2.5-0.5, 2.5-3.8+1.4, head_width=0.1, 
                head_length=0.1, fc='blue', ec='blue', alpha=0.7)
    
    # Feature vector output
    vector_box = FancyBboxPatch((4, 0.5), 6, 1,
                               boxstyle="round,pad=0.1",
                               facecolor='orange',
                               edgecolor='black',
                               linewidth=2)
    ax.add_patch(vector_box)
    
    ax.text(7, 1.2, 'Final Feature Vector (24 dimensions)', ha='center', va='center', 
           fontweight='bold', fontsize=11)
    ax.text(7, 0.8, '[45, 3.82, 0.13, 0.00, 16, 3.15, 1.0, 0.0, 23, 1, 1.0, 3.42, ...]', 
           ha='center', va='center', fontsize=8, style='italic')
    
    # Arrows to final vector
    for _, x_pos, _, _ in categories:
        ax.arrow(x_pos, 2.4, 7-x_pos, 0.5-2.4+0.8, head_width=0.08, 
                head_length=0.1, fc='green', ec='green', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('reports/Figure3b_Feature_Extraction_Detail.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

if __name__ == "__main__":
    print("🎨 Generating Figure 3: Random Forest Edge Inference Pipeline")
    print("=" * 60)
    
    # Generate main pipeline figure
    fig3 = create_rf_inference_pipeline()
    print("✅ Figure 3: RF Inference Pipeline created")
    
    # Generate feature extraction detail
    fig3b = create_feature_extraction_detail()
    print("✅ Figure 3b: Feature Extraction Detail created")
    
    print("\n📁 Files saved:")
    print("   • reports/Figure3_RF_Inference_Pipeline.png")
    print("   • reports/Figure3b_Feature_Extraction_Detail.png")
    
    print("\n📝 LaTeX Caption for Paper:")
    latex_caption = """
\\begin{figure}[htbp]
\\centering
\\includegraphics[width=0.95\\textwidth]{Figure3_RF_Inference_Pipeline.png}
\\caption{Random Forest inference pipeline optimized for real-time edge deployment. The system processes URLs through lexical feature extraction (3.19ms) and Random Forest classification (7.31ms) to achieve sub-11ms total latency. Performance metrics demonstrate edge compliance with 0.26MB model size and 6.23MB total memory footprint, enabling deployment on resource-constrained IoT gateways.}
\\label{fig:rf_inference_pipeline}
\\end{figure}

\\begin{figure}[htbp]
\\centering
\\includegraphics[width=0.95\\textwidth]{Figure3b_Feature_Extraction_Detail.png}
\\caption{Feature extraction pipeline detail showing the transformation of raw URLs into 24-dimensional numerical vectors. The pipeline extracts lexical patterns from URL structure, domain properties, path analysis, and query parameters to create discriminative features for malicious URL detection.}
\\label{fig:feature_extraction_detail}
\\end{figure}
"""
    
    print(latex_caption)
    
    print("\n🎯 Key Benefits of This Figure:")
    print("✅ Focuses on ACTUAL implemented Random Forest (no overclaim)")
    print("✅ Shows precise timing: 3.19ms + 7.31ms = 10.50ms")
    print("✅ Demonstrates edge compliance (0.26MB model, 6.23MB total)")
    print("✅ Matches your validated performance metrics")
    print("✅ Provides clear pipeline visualization for reviewers")
    print("✅ Academic quality suitable for IEEE/Springer journals")