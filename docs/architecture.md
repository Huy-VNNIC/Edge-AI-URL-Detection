# System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IoT Gateway Edge Device                      │
│                      (Raspberry Pi / Jetson Nano)                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌────────────────┐         ┌──────────────────┐                   │
│  │  Network       │────────▶│  URL Detection   │                   │
│  │  Traffic       │         │  Service         │                   │
│  │  (DNS/HTTP)    │         │  (REST API)      │                   │
│  └────────────────┘         └────────┬─────────┘                   │
│                                       │                              │
│                                       ▼                              │
│                        ┌──────────────────────────┐                 │
│                        │  Feature Extraction      │                 │
│                        │  - URL Lexical (12)      │                 │
│                        │  - Domain Metadata (10)  │                 │
│                        │  - DNS Features (5)      │                 │
│                        │  - SSL/TLS (4)           │                 │
│                        └──────────┬───────────────┘                 │
│                                   │                                  │
│                                   ▼                                  │
│                        ┌──────────────────────────┐                 │
│                        │  Random Forest Classifier │                 │
│                        │  - 100 estimators         │                 │
│                        │  - 1.8 MB model          │                 │
│                        │  - 7.31 ms inference     │                 │
│                        └──────────┬───────────────┘                 │
│                                   │                                  │
│                                   ▼                                  │
│                        ┌──────────────────────────┐                 │
│                        │  Detection Result        │                 │
│                        │  - Malicious/Benign      │                 │
│                        │  - Confidence Score      │                 │
│                        │  - Processing Time       │                 │
│                        └──────────┬───────────────┘                 │
│                                   │                                  │
│  ┌────────────────────────────────┴────────────────────────────┐   │
│  │                                                               │   │
│  ▼                          ▼                        ▼          │   │
│ ┌──────────┐        ┌──────────────┐        ┌─────────────┐   │   │
│ │ Firewall │        │  SIEM/Logs   │        │ Prometheus  │   │   │
│ │ Block    │        │  (Splunk)    │        │ Metrics     │   │   │
│ └──────────┘        └──────────────┘        └─────────────┘   │   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Network Traffic Ingestion
- Captures DNS queries and HTTP/HTTPS requests
- Extracts URLs from network packets
- Rate limiting: 137 samples/second

### 2. Feature Extraction Engine (3.19 ms)
- **URL Lexical Analysis**: Length, entropy, special characters
- **Domain Metadata**: WHOIS, age, registration period
- **DNS Lookup**: Response time, TTL, A records
- **SSL/TLS Verification**: Certificate validity, issuer

### 3. ML Detection Engine (7.31 ms)
- Pre-trained Random Forest model (100 trees)
- StandardScaler normalization
- 31-dimensional feature vector input
- Binary classification output

### 4. Action Layer
- **Block Mode**: Firewall integration
- **Alert Mode**: SIEM forwarding
- **Monitor Mode**: Logging only

## Data Flow

```
URL Input → Feature Extraction → Normalization → Random Forest → Decision
  (0ms)         (3.19ms)           (0ms)          (7.31ms)      (10.50ms total)
```

## Deployment Modes

### Mode 1: Inline DNS Filtering
```
Client → DNS Query → [Gateway + ML] → Allow/Block → Upstream DNS
```

### Mode 2: HTTP Proxy
```
Client → HTTP Request → [Gateway + ML] → Filter → Web Server
```

### Mode 3: SIEM Integration
```
Network Traffic → [Gateway + ML] → Detection Events → Splunk/ELK
```

## Performance Characteristics

| Component | Latency | Memory | Throughput |
|-----------|---------|--------|------------|
| Feature Extraction | 3.19 ms | 1.0 MB | 313 samples/s |
| Model Inference | 7.31 ms | 2.5 MB | 137 samples/s |
| API Overhead | 0.1 ms | 0.5 MB | - |
| **Total System** | **10.50 ms** | **3.5 MB** | **137 samples/s** |

## Technology Stack

- **ML Framework**: scikit-learn 1.3.0
- **API Framework**: FastAPI 0.104.0
- **Feature Processing**: pandas, numpy
- **DNS Resolution**: dnspython
- **SSL Verification**: OpenSSL via Python ssl
- **Monitoring**: Prometheus client
- **Containerization**: Docker 24.0+
- **Target Platform**: ARM Cortex-A53+ / x86-64
