FROM apache/airflow:latest

# Cài thêm provider & lib cần cho task Python
USER root
RUN apt-get update && apt-get install -y curl jq netcat && rm -rf /var/lib/apt/lists/*

USER airflow
# Providers (nếu cần DockerOperator hoặc Kafka, HTTP…)
COPY requirements.txt /requirements.txt
RUN pip install --user  --upgrade pip 
RUN pip install --no-cache-dir --user -r /requirements.txt




# RUN pip install --no-cache-dir \
#     apache-airflow-providers-http==4.7.0 \
#     apache-airflow-providers-cncf-kubernetes==9.0.0 \
#     kafka-python==2.0.2 \
#     requests==2.32.3 \
#     python-dotenv==1.0.1

# # (tuỳ chọn) Nếu bạn muốn submit Flink SQL từ Airflow bằng PyFlink client
# RUN pip install --no-cache-dir apache-flink==1.19.1