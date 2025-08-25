FROM apache/airflow:latest

# Cài thêm provider & lib cần cho task Python
USER root
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        curl \
        jq \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

USER airflow
# Providers (nếu cần DockerOperator hoặc Kafka, HTTP…)
COPY requirements.txt /requirements.txt
# RUN pip install --user  --upgrade pip 
# RUN pip install --no-cache-dir --user -r /requirements.txt
# RUN pip install --no-cache-dir -r /requirements.txt
# Nâng cấp pip, setuptools, wheel để tránh lỗi build
# Cài Airflow trước với version cố định
RUN pip install apache-airflow==3.0.4 --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.4/constraints-3.12.txt"

# Sau đó mới cài requirements khác
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir




# RUN pip install --no-cache-dir \
#     apache-airflow-providers-http==4.7.0 \
#     apache-airflow-providers-cncf-kubernetes==9.0.0 \
#     kafka-python==2.0.2 \
#     requests==2.32.3 \
#     python-dotenv==1.0.1

# # (tuỳ chọn) Nếu bạn muốn submit Flink SQL từ Airflow bằng PyFlink client
# RUN pip install --no-cache-dir apache-flink==1.19.1