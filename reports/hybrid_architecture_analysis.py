"""
EDGE-AI HYBRID/ENSEMBLE ARCHITECTURE ANALYSIS
=============================================

🎯 HYBRID/ENSEMBLE DECISION PIPELINE CỦA BẠN:

1. KIẾN TRÚC HYBRID (3 MODELS):
   ├─ Random Forest (PRIMARY) - Lexical Features
   ├─ Transformer (OPTIONAL) - URL Sequence Analysis  
   └─ GNN (OPTIONAL) - Domain Relationship Graphs

2. ENSEMBLE DECISION LOGIC:
   ├─ Majority Vote: np.round(np.mean(predictions))
   ├─ Probability Averaging: np.mean(probabilities)  
   └─ Confidence: max(prob, 1-prob)

3. FALLBACK STRATEGY:
   ├─ RF Always Active (Edge Deployment)
   ├─ Transformer/GNN Optional (Resource Available)
   └─ Graceful Degradation (Single Model OK)

4. PRODUCTION DEPLOYMENT:
   ✅ Current: RF-only (10.50ms offline, 203ms API)
   🔄 Future: RF+Transformer+GNN ensemble
   📊 Adaptive: Resource-based model selection
"""

# ========================================
# VISUAL ARCHITECTURE DIAGRAM (ASCII ART)
# ========================================

HYBRID_ARCHITECTURE_DIAGRAM = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EDGE-AI HYBRID URL DETECTION PIPELINE                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

INPUT: URL
   │
   ▼
┌─────────────────┐
│  URL PARSING    │ ──► Domain, Path, Query, etc.
└─────────────────┘
   │
   ├──────────────────────┬──────────────────────┬─────────────────────┐
   ▼                      ▼                      ▼                     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ LEXICAL     │    │ SEQUENCE    │    │ GRAPH       │    │ METADATA    │
│ FEATURES    │    │ TOKENS      │    │ STRUCTURE   │    │ FEATURES    │
│             │    │             │    │             │    │             │
│• Length     │    │• Char-level │    │• Domain     │    │• DNS TTL    │
│• Entropy    │    │• Attention  │    │• SSL Cert   │    │• WHOIS      │
│• Suspicious │    │• Position   │    │• Network    │    │• Age        │
│  patterns   │    │  encoding   │    │  topology   │    │• Registrar  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
   │                      │                      │                     │
   ▼                      ▼                      ▼                     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐         ┌──────┐
│ RANDOM      │    │TRANSFORMER  │    │    GNN      │         │ABLATION│
│ FOREST      │    │   MODEL     │    │   MODEL     │         │STUDY │
│             │    │             │    │             │         │      │
│100 trees    │    │• Attention  │    │• Graph Conv │         │AUC=  │
│Max depth 20 │    │• Embeddings │    │• Message    │ ────────┤0.5000│
│Balanced     │    │• Sequences  │    │  Passing    │         │      │
│0.26MB       │    │• Context    │    │• Pooling    │         └──────┘
└─────────────┘    └─────────────┘    └─────────────┘
   │                      │                      │
   │    ┌─────────────────────────────────────────┘
   │    │                 │
   ▼    ▼                 ▼
┌──────────────────────────────────────┐
│        ENSEMBLE DECISION              │
│                                      │
│  🔥 MAJORITY VOTE:                   │
│     final_pred = round(mean(preds))  │
│                                      │
│  📊 PROBABILITY AVERAGING:           │
│     final_prob = mean(probabilities) │
│                                      │  
│  🎯 CONFIDENCE SCORE:                │
│     confidence = max(prob, 1-prob)   │
│                                      │
│  ⚡ ADAPTIVE LOADING:                │
│     • Always: Random Forest          │
│     • Optional: Transformer + GNN    │
│     • Fallback: Single model OK      │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│           FINAL OUTPUT               │
│                                      │
│  • Prediction: 0 (benign) / 1 (mal) │
│  • Probability: [0.0, 1.0]          │
│  • Label: "benign" / "malicious"     │
│  • Confidence: [0.5, 1.0]           │
│  • Ensemble Size: 1-3 models        │
└──────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────┐
│         EDGE DEPLOYMENT              │
│                                      │
│  📱 Current Production:              │
│     • RF-only: 10.50ms offline      │
│     • API: 203.23ms end-to-end      │
│     • Memory: 6.23MB total          │
│     • Success: 100% reliability     │
│                                      │
│  🚀 Future Scaling:                  │ 
│     • RF+Transformer: Medium load   │
│     • RF+TF+GNN: High resources     │
│     • Auto-adaptation by hardware   │
└──────────────────────────────────────┘
"""

print("🎯 HYBRID/ENSEMBLE ARCHITECTURE ANALYSIS")
print("="*50)
print(__doc__)
print("\n" + "="*80)
print("📊 VISUAL PIPELINE DIAGRAM")
print("="*80)
print(HYBRID_ARCHITECTURE_DIAGRAM)