FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3.7-dev \
    python3.7-venv \
    python3-setuptools \
    python3-pip

# set python3.7 as default for relevant python commands
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 && \
    update-alternatives --set python /usr/bin/python3.7 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1 && \
    update-alternatives --set python3 /usr/bin/python3.7

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    gcc \
    curl \
    lsb-release \
    wget \
    git \
    gnupg \
    bash \
    procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get remove -y \
    g++ \
    wget \
    git \
    lsb-release \
    gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && \
    pip3 install seldon-core==v1.13.1 google-cloud-storage==1.36.0 werkzeug==2.0.3 joblib==1.1.0 lightgbm numpy

WORKDIR /app

COPY MyModel.py /app
COPY lgb.pkl /app
COPY run_seldon.sh /app
COPY ServeSeldon.py /app

ENV SELDON_ENTRYPOINT ServeSeldon
ENV MODEL_NAME MyModel
ENV SERVICE_TYPE MODEL
ENV PERSISTENCE 0

RUN chmod 755 /app/run_seldon.sh

ENTRYPOINT /app/run_seldon.sh
