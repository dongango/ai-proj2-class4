# 베이스 이미지 (Anaconda 기반)
FROM continuumio/anaconda3

# 작업 디렉토리 생성
WORKDIR /app

# 소스 카피..
COPY environment.yml ./
COPY conda-requirements.txt ./

# 빌드 도구 설치 (for psutil wordcloud)
RUN apt-get update && \
    apt-get install -y build-essential python3-dev libjpeg-dev zlib1g-dev && \
    apt-get clean

# python 3.11 로 conda 이미지 생성
RUN conda env create -f environment.yml && conda clean -afy
SHELL ["conda", "run", "-n", "py311", "/bin/bash", "-c"]

# py311 환경으로 전환
# RUN conda deactivate
# RUN conda activate py311

# 의존성 설치
RUN pip install --no-cache-dir -r conda-requirements.txt
RUN pip install pymysql

# tensorflow 설치
RUN conda install tensorflow=2.12

# py311 환경을 기본으로 상요..
RUN echo "conda activate py311" >> /root/.bashrc

# 대신 shell script 사용
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# tensorflow 버젼확인
RUN echo "Tensorflow version : "
RUN python -c "import tensorflow as tf; print(tf.__version__)"


