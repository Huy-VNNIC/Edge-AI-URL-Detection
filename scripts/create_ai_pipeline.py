import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

# Define colors
input_color = '#E3F2FD'
feature_color = '#FFF3E0'
ai_color = '#E8F5E8'
output_color = '#FCE4EC'

# Input Stage
input_box = FancyBboxPatch((0.5, 6), 1.5, 1.2, boxstyle="round,pad=0.1", 
                          facecolor=input_color, edgecolor='black', linewidth=2)
ax.add_patch(input_box)
ax.text(1.25, 6.6, 'Raw Input\n• URLs\n• DNS Queries\n• SSL Metadata', 
        ha='center', va='center', fontsize=10, fontweight='bold')

# Feature Engineering Stage
feature_box = FancyBboxPatch((3, 5.5), 2.5, 2.2, boxstyle="round,pad=0.1",
                            facecolor=feature_color, edgecolor='black', linewidth=2)
ax.add_patch(feature_box)
ax.text(4.25, 6.6, 'AI Feature Engineering\n• URL Lexical (51.5%)\n• Domain Metadata (33.8%)\n• SSL/Security (8.8%)\n• DNS Features (5.9%)\n31-Dimensional Vector', 
        ha='center', va='center', fontsize=10, fontweight='bold')

# AI Model Stage (Highlighted)
ai_box = FancyBboxPatch((6.5, 5), 2.5, 3.2, boxstyle="round,pad=0.1",
                       facecolor=ai_color, edgecolor='red', linewidth=3)
ax.add_patch(ai_box)
ax.text(7.75, 6.6, 'AI Model Ensemble\n• Random Forest (Optimal)\n• XGBoost (Compact)\n• Neural Network\n• Logistic Regression\n• SVM\nInference: 2.36-36.94ms', 
        ha='center', va='center', fontsize=10, fontweight='bold')

# Decision Output
output_box = FancyBboxPatch((3, 2.5), 2.5, 1.5, boxstyle="round,pad=0.1",
                           facecolor=output_color, edgecolor='black', linewidth=2)
ax.add_patch(output_box)
ax.text(4.25, 3.25, 'AI Decision\n• Benign/Malicious\n• Confidence Score\n• 100% Accuracy', 
        ha='center', va='center', fontsize=10, fontweight='bold')

# Edge Deployment Box
edge_box = FancyBboxPatch((6.5, 1.5), 2.5, 2.5, boxstyle="round,pad=0.1",
                         facecolor='#F3E5F5', edgecolor='blue', linewidth=2)
ax.add_patch(edge_box)
ax.text(7.75, 2.75, 'Edge Deployment\n• Memory: <6.23MB\n• Latency: <11ms\n• Throughput: 262K/sec\n• IoT Gateway Ready', 
        ha='center', va='center', fontsize=10, fontweight='bold')

# Arrows
# Input to Feature
arrow1 = ConnectionPatch((2, 6.6), (3, 6.6), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="black")
ax.add_artist(arrow1)

# Feature to AI
arrow2 = ConnectionPatch((5.5, 6.6), (6.5, 6.6), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="red", linewidth=2)
ax.add_artist(arrow2)

# AI to Decision
arrow3 = ConnectionPatch((7.75, 5), (4.25, 4), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="black")
ax.add_artist(arrow3)

# AI to Edge
arrow4 = ConnectionPatch((7.75, 5), (7.75, 4), "data", "data",
                        arrowstyle="->", shrinkA=5, shrinkB=5, mutation_scale=20, fc="blue")
ax.add_artist(arrow4)

# Title
ax.text(5, 7.5, 'Edge-AI Malicious URL Detection Pipeline', 
        ha='center', va='center', fontsize=16, fontweight='bold')

# AI Highlight Label
ax.text(7.75, 4.5, 'AI CORE', ha='center', va='center', 
        fontsize=12, fontweight='bold', color='red',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig('/home/dtu/project_URL/Edge-AI-URL-Detection/paper/latex/ai_pipeline_detailed.png', 
            dpi=300, bbox_inches='tight')
plt.close()

print("AI Pipeline diagram saved successfully!")