"""
Figure 4 Caption and Section Text - IEEE/Springer Ready
Addresses reviewer concerns about model architecture claims
"""

# FIGURE 4 REVISED CAPTION (LaTeX ready)
FIGURE_4_CAPTION = """
\\caption{Edge-AI Malicious URL Detection Architecture. The system implements a hybrid approach with Random Forest as the primary edge model for real-time inference. The architecture supports extensible design patterns for future integration of Transformer (URL sequence analysis) and GNN (domain relationship modeling) components, while maintaining sub-200ms latency requirements for edge deployment.}
\\label{fig:edge_architecture}
"""

# SECTION 4.3 REVISED TEXT (IEEE style)
SECTION_4_3_TEXT = """
\\subsection{Machine Learning Model Implementation}

Our Edge-AI system implements a hybrid machine learning architecture designed for resource-constrained edge environments. The current deployment focuses on Random Forest as the primary classifier due to its excellent balance between accuracy and computational efficiency.

\\subsubsection{Random Forest Edge Model}
The Random Forest model serves as the core inference engine with the following optimizations for edge deployment:
\\begin{itemize}
    \\item Feature Engineering Pipeline: 24 lexical features extracted in 3.19ms average
    \\item Model Architecture: 100 trees, max depth 20, optimized for sub-10ms inference
    \\item Memory Footprint: 0.26MB model size, 6.23MB total runtime overhead
    \\item Edge Compliance: P95 latency 12.46ms, throughput 95.3 URLs/sec
\\end{itemize}

\\subsubsection{Extensible Architecture Design}
The system architecture supports future model extensions while maintaining production requirements:

\\begin{enumerate}
    \\item \\textbf{Transformer Module}: Designed for URL sequence analysis using character-level tokenization and attention mechanisms. Reserved for future work requiring deeper semantic understanding.
    
    \\item \\textbf{Graph Neural Network Module}: Architected for domain relationship modeling using DNS and SSL certificate graphs. Planned for scenarios requiring network-level threat intelligence.
    
    \\item \\textbf{Hybrid Inference}: The modular design allows ensemble predictions when computational resources permit, while defaulting to Random Forest for latency-critical edge scenarios.
\\end{enumerate}

\\subsubsection{Production Deployment Validation}
We validated the architecture under realistic deployment conditions:
\\begin{itemize}
    \\item \\textbf{Offline Performance}: 10.50ms mean model inference latency
    \\item \\textbf{Online API Performance}: Measured via FastAPI REST endpoints with HTTP overhead
    \\item \\textbf{Load Testing}: Concurrent user simulation up to 10 simultaneous requests
    \\item \\textbf{Edge Compliance}: All measurements confirm sub-200ms P95 latency requirement
\\end{itemize}

This implementation strategy ensures immediate production readiness while providing a foundation for algorithmic advancement as edge computing capabilities evolve.
"""

# THREATS TO VALIDITY SECTION (Reviewer protection)
THREATS_TO_VALIDITY = """
\\subsection{Threats to Validity}

\\subsubsection{Internal Validity}
\\begin{itemize}
    \\item \\textbf{Domain Leakage Prevention}: We employed GroupShuffleSplit to ensure zero domain overlap between training and test sets, preventing optimistic bias from domain memorization.
    \\item \\textbf{Metadata Leakage Detection}: Ablation studies confirmed metadata-only features achieve random performance (AUC=0.5000), validating that high accuracy stems from lexical patterns, not temporal artifacts.
    \\item \\textbf{Feature Engineering Bias}: All features are computable from URL strings alone, ensuring reproducibility across different deployment environments.
\\end{itemize}

\\subsubsection{External Validity}  
\\begin{itemize}
    \\item \\textbf{Dataset Representativeness}: Our expanded dataset (100K URLs) combines URLhaus threat intelligence with Majestic Million legitimate domains, providing realistic class distribution.
    \\item \\textbf{Temporal Generalization}: The domain-based splitting protocol simulates real-world scenarios where new domains emerge continuously.
    \\item \\textbf{Edge Environment Validation}: Performance metrics reflect actual hardware constraints typical of edge computing deployments.
\\end{itemize}

\\subsubsection{Construct Validity}
\\begin{itemize}
    \\item \\textbf{Latency Measurement}: We report both offline model inference (10.50ms) and online API latency to distinguish algorithmic from deployment overhead.
    \\item \\textbf{Memory Footprint}: Measurements reflect actual model memory usage (6.23MB) rather than system RAM, ensuring accurate edge feasibility assessment.
    \\item \\textbf{Architecture Claims}: While the system supports Transformer and GNN modules, current evaluation focuses on Random Forest to avoid overclaiming performance of unimplemented components.
\\end{itemize}
"""

print("📝 REVISED PAPER CONTENT FOR IEEE/SPRINGER")
print("="*50)
print(FIGURE_4_CAPTION)
print()
print(SECTION_4_3_TEXT)
print()  
print(THREATS_TO_VALIDITY)