<h1 align="center"> Emotional Pulse Stream</a></h1>

<div align="center"> 

[![License](https://img.shields.io/badge/LICENSE-MIT_License-orange.svg)](https://opensource.org/license/mit) 
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/) 
[![Linkedin URL](https://img.shields.io/badge/LinkedIn-Follow-blue?logo=linkedin)]()
[![Flink](https://img.shields.io/badge/Flink-Flink-007bff?style=flat-square&logo=apache-flink)](https://flink.apache.org/)
[![Kibana](https://img.shields.io/badge/Kibana-Kibana-005571?style=flat-square&logo=kibana)](https://www.elastic.co/kibana/)
[![Grafana](https://img.shields.io/badge/Grafana-Grafana-F46800?style=flat-square&logo=grafana)](https://grafana.com/)
[![Kafka](https://img.shields.io/badge/Kafka-Kafka-231F20?style=flat-square&logo=apache-kafka)](https://kafka.apache.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-Elasticsearch-005571?style=flat-square&logo=elasticsearch)](https://www.elastic.co/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostgreSQL-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)

</div>

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Usage](#-usage)
- [Dashboards](#-dashboards)
- [Future Work](#-furture-work)
- [Contributors](#-contributors)
- [License](#-license)

---

## ✨ Overview
**Emotional Pulse Stream** is an end-to-end **real-time data engineering pipeline** that captures livestream comments, processes them, and analyzes their **sentiment and emotional pulse** in real time.  

This project demonstrates how to combine **streaming, data storage, AI/ML sentiment analysis, and observability** into a single containerized system.  

---

## ✨ Features
- **Data Ingestion**: Collects livestream comments from API crawlers (e.g., TikTok).
- **Streaming Platform (Kafka)**: Distributed message broker for scalability.
- **Stream Processing (Flink + Python)**: Real-time processing and sentiment analysis.
- **Storage**: 
  - **PostgreSQL** → structured data (comments, users, sentiment).
  - **Elasticsearch** → log/search engine for fast queries.
- **Visualization**: 
  - **Kibana** → dashboards for logs and text analytics.
  - **Grafana** → system metrics visualization.
- **Observability**: 
  - **Prometheus** → collects metrics.
  - **OpenTelemetry** → tracing and logging.
- **Orchestration (Airflow)**: DAGs for ETL, scheduling, and model retraining.
- **Docker Compose**: Containerized setup for reproducibility.

---

## 🏗️ System Architecture
![Architecture](./docs/assets/EpStream_Project_Architecture.svg)




---

## 🚀 Tech Stack
- **Languages**: Python, SQL
- **Streaming**: Apache Kafka, Apache Flink (PyFlink)
- **Storage**: PostgreSQL, Elasticsearch
- **Visualization**: Kibana, Grafana
- **Orchestration**: Apache Airflow
- **Monitoring**: Prometheus, OpenTelemetry
- **Containerization**: Docker, Docker Compose

---

## 📂 Project Structure

```bash
emotional-pulse-stream/
├── airflow/                # Airflow DAGs & configs
│   └── dags/
├── dockers/                  
│   └── flink/              # Flink jobs (Python)
│        └── sentiment_job.py

│   └── kafka/                  # Kafka configs
│   │    └── Dockerfile
├── collectors/                # Livestream API comment's crawler
│   └── main.py
├── models/                 # Sentiment models / ML
│   └── sentiment_model.pkl
├── tests/                 # Testing services by manually running
│   └── test_....py
├── monitoring/             # Prometheus + Grafana configs
├── storage/                # PostgreSQL, Elasticsearch configs
├── docker-compose.yml      # Master docker-compose file
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
└── README.md

```

## ⚙️ Getting Started
**Prerequisites**
- [Docker]() and [Docker Compose]()
- [Python 3.9+]()
- A virtual environment tool like ``venv`` or ``uv``.

**Installation Steps**

1. Clone Repository
```bash
git clone https://github.com/tph-kds/epStream
cd epStream
```

2. Set up the Python environment:
Create and active a virtual environment using your preferred tool.

- Using ``venv`` (standard library):
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

```


- Using ``uv``:
```bash
uv init
uv venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

```

3. Install dependencies:
```bash
pip install -r requirements.txt
# Or, if using uv:
# uv pip install -r requirements.txt

```

4. Lauch the services:
Start the entire pipeline using Docker Compose. This command will build and start all services in detached mode.

```bash
docker-compose up -d
```
This will start running some services as the ones above:
- Kafka + Zookeeper

- Flink JobManager + TaskManagers

- PostgreSQL + Elasticsearch

- Airflow

- Prometheus + Grafana

- Kibana


---

## 📊 Usage

**Start Data Pipeline**:
The crawler pushes comments → Kafka → Flink → PostgreSQL/Elasticsearch.

**View Logs & Analytics**:

- Kibana → http://localhost:5601

- Grafana → http://localhost:3000

- Airflow UI: http://localhost:8080 (default user: airflow, pass: airflow)

--- 

## 📈 Dashboards

- **Kibana Dashboard**: Visualize and analyze the processed comment data. Create dashboards to search, filter, and aggregate comments by sentiment, emotion, or keywords in real time.

- **Grafana Dashboard**: Monitor the health and performance of the entire data pipeline. Track metrics such as Kafka message throughput, Flink processing latency, and CPU/memory usage of all services.

---

## 🧠 Future Work

Future enhancements planned for the project include:

- [ ] Multilingual Model Integration: Add support for sentiment and emotion analysis in multiple languages.

- [ ] Real-Time Anomaly Detection: Implement algorithms to automatically detect unusual events, such as coordinated spam or sudden spikes in negative sentiment.

- [ ] Kubernetes Deployment: Create Helm charts and configurations for deploying the pipeline on a Kubernetes cluster for enhanced scalability and resilience.

- [ ] Advanced Analytics: Introduce topic modeling and named entity recognition (NER) to extract deeper insights from the comment stream.

---

## 🙌 Contributors
Contributions are welcome! If you have an idea for an improvement or have found a bug, please feel free to open an issue or submit a pull request. We appreciate all contributions, from bug reports to new features.

Thank you to all the contributors who have invested their time in this project.

---

## ⚖️ License

This project is licensed under the [MIT License](https://github.com/tph-kds/epStream/blob/main/LICENSE). See the `LICENSE` file for more details.

