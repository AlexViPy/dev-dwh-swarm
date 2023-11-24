FROM python:3.10-slim-bullseye as builder
RUN pip install --upgrade pip
RUN pip install -U requests

COPY main.py main.py
CMD ["python", "main.py"]