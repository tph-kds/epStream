# FROM flink:2.1.0-scala_2.12-java21
FROM flink:2.0.0-scala_2.12-java17

USER root

# Install Python and SSL dependencies
RUN apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update -y -o Acquire::Retries=5 \
    && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev \
    openssl ca-certificates wget curl zip \
    && rm -rf /var/lib/apt/lists/*

# Update CA certificates
RUN update-ca-certificates

# Ensure python command points to python3
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /opt/flink
COPY ./requirements.txt .

# Upgrade pip first
RUN pip install --upgrade pip

# Install Apache Airflow with constraints
RUN pip install --default-timeout=1000 --retries=20 --no-cache-dir \
    apache-airflow==3.0.4 \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.0.4/constraints-3.12.txt" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# Install other packages with high timeout and retries
RUN pip install --default-timeout=1000 --retries=30 --no-cache-dir \
    -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# Copy and run connector download script
COPY dockers/flink/download_libs.sh /opt/flink/download_libs.sh
RUN chmod +x /opt/flink/download_libs.sh && bash -x /opt/flink/download_libs.sh

# Copy processors (your Python code)
COPY ./processors/ /opt/flink/processors/

USER flink
