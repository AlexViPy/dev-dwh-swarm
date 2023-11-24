FROM python:3.10-slim-bullseye
RUN pip install --upgrade pip
RUN pip install -U requests

COPY . .
CMD ["python", "main.py"]