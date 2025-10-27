# 🧠 Edge-AI Real-Time Malicious Domain & URL Detection in IoT Gateway Environments

![System Architecture](https://res.cloudinary.com/dh41tyuha/image/upload/v1761564853/Screenshot_from_2025-10-27_20-33-13_akxnb3.png)

## 🚀 Overview
This project proposes an **Edge-AI framework** for detecting **malicious domains and URLs** in **IoT gateway environments** using **hybrid multi-feature analysis** and **containerized edge deployment** (Docker).

Unlike traditional cloud-based detection, this system runs directly on **edge devices** (e.g., Raspberry Pi, mini servers) to provide:
- ⚡ Real-time response with low latency  
- 🧩 Hybrid feature extraction (Traffic + DNS + SSL + URL Lexical)  
- 🧠 Multi-model ensemble (Random Forest + Transformer + GNN)  
- 🐳 Containerized modular design with Docker Compose  

---

## 🏗️ System Architecture

### **Input**
- **Packet/IP Traffic** (captured using Zeek/tcpdump)  
- **DNS Queries** (via dnsmasq or BIND logs)  
- **SSL Certificates Metadata** (via sslscan / CT logs / WHOIS)  
- **URL Lexical Features** (tokens, entropy, length, special characters)

### **Processing Pipeline (Edge Gateway)**
1. **ETL Module** – Collects and parses traffic, DNS, and SSL logs.  
2. **Feature Extractor** – Combines flow, DNS, SSL, and URL lexical data into unified vectors.  
3. **Machine Learning Ensemble** –  
   - `Random Forest`: tabular hybrid features  
   - `Transformer`: semantic & lexical URL analysis  
   - `Graph Neural Network (GNN)`: domain–IP–resolver query graph analysis  
4. **Decision Engine** – Generates `Benign` or `Malicious` labels in real-time.  

### **Output**
- ✅ Benign or ❌ Malicious Classification  
- Real-time alert API (JSON/REST)  
- Local dashboard: latency, CPU/RAM usage, accuracy metrics  

---

## ⚙️ Deployment Setup

### **Docker Compose Structure**
```bash
version: "3.8"
services:
  zeek: ...
  dnsmasq: ...
  etl: ...
  enricher: ...
  model_rf: ...
  model_transformer: ...
  model_gnn: ...
  api: ...
  prometheus:
  grafana:
```

Run the stack:

```bash
docker compose up -d
```

### **Hardware**

* Raspberry Pi 4 / Edge Server (ARM64 or x86_64)
* Minimum: 4 GB RAM, 32 GB SD Card

---

## 📊 Dataset Sources

| Source                                                                | Description                      |
| --------------------------------------------------------------------- | -------------------------------- |
| [TON-IoT](https://research.unsw.edu.au/projects/toniot-datasets)      | IoT & Edge logs and telemetry    |
| [Edge-IIoTset](https://www.techrxiv.org/users/683379/articles/678449) | Realistic industrial IoT traffic |
| [CICIDS2017 / UNSW-NB15](https://www.unb.ca/cic/datasets/)            | Network flow baseline data       |
| [URLHaus](https://urlhaus.abuse.ch/)                                  | Malicious URL database           |
| [PhishTank](https://phishtank.org/)                                   | Phishing domains                 |
| Certificate Transparency Logs                                         | SSL metadata and issuer info     |
| WHOIS / RDAP                                                          | Domain registration details      |

---

## 📈 Evaluation Metrics

| Metric                                 | Description                     |
| -------------------------------------- | ------------------------------- |
| **Accuracy / Precision / Recall / F1** | ML model performance            |
| **Latency (ms)**                       | Time from capture → detection   |
| **CPU / RAM usage**                    | Edge resource monitoring        |
| **False Positive Rate**                | Practical reliability indicator |

---

## 🔬 Research Objective

This project addresses the research gap in:

* Real-time domain & URL threat detection **directly at the edge**
* Integrating **traffic, DNS, SSL, and lexical** features
* Containerized **AI ensemble** on low-power IoT gateways

---

## 📚 Citation

If you use this framework in academic work:

```
Nguyen Nhat Huy. (2025). Edge-AI Real-Time Malicious Domain & URL Detection in IoT Gateway Environments using Hybrid Traffic/DNS/SSL Features. Chungbuk National University.
```

---

## 👨‍💻 Author

**Nguyen Nhat Huy**
Department of Software, Chungbuk National University
📧 [nguyennhathuybdi06@gmail.com](mailto:nguyennhathuybdi06@gmail.com)
🌐 [https://github.com/nguyennhathuy](https://github.com/nguyennhathuy)

---

> “Deploying intelligence where data originates — the Edge.”
