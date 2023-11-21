FROM apache/airflow:2.7.2

# Become root to install requirements
USER root

RUN apt-get update && apt-get install -y libpq-dev python-dev
ADD --chown=airflow:airflow requirements.txt requirements.txt

USER airflow
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
