# IEEE ACCESS COVER LETTER - READY FOR SUBMISSION

**Subject:** Submission of Manuscript to IEEE Access: "Edge-AI Malicious Domain and URL Detection for IoT Gateway Security: A Lightweight Random Forest Approach"

---

**Dear Editor-in-Chief,**

We are pleased to submit our manuscript entitled **"Edge-AI Malicious Domain and URL Detection for IoT Gateway Security: A Lightweight Random Forest Approach"** for consideration for publication in **IEEE Access**.

## **Paper Summary**

This work addresses a critical gap in IoT security by proposing a complete Edge-AI system for real-time malicious URL detection deployed directly at IoT gateways. Unlike existing cloud-based solutions, our approach operates with **sub-11ms inference latency** and **6.23MB memory footprint**, making it suitable for resource-constrained edge environments.

## **Key Contributions**

1. **Complete Edge-AI Architecture**: A production-ready system with containerized deployment and RESTful API interface
2. **Hybrid Feature Engineering**: Novel integration of URL lexical, DNS behavioral, SSL certificate, and domain metadata features
3. **Rigorous Performance Validation**: Comprehensive evaluation including offline inference (10.50ms), online API performance (203ms), and memory profiling on actual IoT hardware
4. **Real-world Feasibility**: Demonstrated on 100,000 URLs with 99.31% accuracy and practical deployment constraints

## **Technical Innovation**

The paper makes several technical advances:
- **Privacy-preserving feature extraction** without raw payload inspection
- **Lightweight Random Forest optimization** for edge deployment constraints  
- **Transparent measurement methodology** enabling reproducibility
- **Production-grade implementation** with full API benchmarking

## **Experimental Rigor**

Our evaluation follows rigorous experimental protocols:
- Large-scale dataset (100,000 URLs) with balanced class distribution
- Domain-based splitting to prevent data leakage
- Both offline algorithmic and online system-level performance measurement
- Detailed memory profiling and latency breakdown analysis
- Statistical validation with confidence intervals

## **Relevance to IEEE Access**

This work aligns perfectly with IEEE Access scope in:
- **IoT Security**: Addressing practical security challenges in IoT deployments
- **Edge Computing**: Demonstrating feasible edge-AI implementation with measured performance
- **Machine Learning Applications**: Practical ML deployment with comprehensive evaluation
- **Cybersecurity**: Real-world threat detection with validated effectiveness

## **Impact and Applications**

The proposed system addresses the immediate need for:
- **Real-time threat detection** in IoT environments
- **Privacy-preserving security** without cloud dependency  
- **Resource-efficient AI** suitable for edge deployment
- **Scalable cybersecurity** for growing IoT ecosystems

## **Novelty Statement**

While URL detection has been extensively studied, this work uniquely combines:
1. **Edge-specific optimization** with rigorous latency and memory constraints
2. **Complete system implementation** rather than algorithmic-only evaluation
3. **Hybrid multi-source feature engineering** optimized for edge processing
4. **Production-grade validation** with RESTful API and containerized deployment

## **Author Qualifications**

The authors have extensive experience in:
- Edge computing and IoT security research
- Machine learning system optimization
- Cybersecurity threat detection
- Performance evaluation and benchmarking

## **Compliance Statement**

We confirm that:
- This work is original and has not been submitted elsewhere
- All experimental procedures follow ethical guidelines
- Source code and datasets will be made available upon acceptance
- No conflicts of interest exist

## **Suggested Reviewers**

We respectfully suggest the following reviewers with expertise in edge computing, IoT security, and machine learning:

1. **Dr. [Reviewer Name]** - [University], expert in edge-AI and IoT security
2. **Prof. [Reviewer Name]** - [Institution], specialist in malware detection and machine learning
3. **Dr. [Reviewer Name]** - [Organization], authority on edge computing and cybersecurity

## **Conclusion**

This manuscript presents a timely and practical solution to an important IoT security challenge. The comprehensive experimental validation, production-ready implementation, and rigorous performance measurement make it suitable for the broad interdisciplinary audience of IEEE Access.

We believe this work will be of significant interest to researchers and practitioners in edge computing, IoT security, and practical machine learning deployment. We look forward to your positive consideration.

Thank you for your time and consideration.

**Sincerely,**

**Phan Luu Tung and Nguyen Nhat Huy**  
Department of Computer Science  
Duy Tan University  
Da Nang, Vietnam  
Email: nguyennhathuy11@dtu.edu.vn  
[Date]

**Source Code Availability:**
Complete implementation available at: https://github.com/Huy-VNNIC/Edge-AI-URL-Detection

---

## **Manuscript Statistics**
- **Length**: ~12 pages (IEEE Access format)
- **Figures**: 5 (all original, publication-ready)
- **References**: 16 (high-quality, recent)
- **Keywords**: Edge computing, IoT security, malicious URL detection, Random Forest, machine learning, cybersecurity

## **Files Included**
1. `main.tex` - Complete manuscript in LaTeX format
2. `references.bib` - BibTeX reference file  
3. `figure1_architecture.png` - System architecture diagram
4. `figure2_features.png` - Feature extraction pipeline
5. `figure3_rf_pipeline.png` - Random Forest inference pipeline
6. `figure4_evaluation_setup.png` - Experimental setup
7. `figure5_performance_results.png` - Performance evaluation results