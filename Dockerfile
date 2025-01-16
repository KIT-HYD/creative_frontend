FROM python:3.12

COPY metacatalog-api /app/metacatalog-api
WORKDIR /app/metacatalog-api
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install debugpy

COPY src /app
WORKDIR /app

CMD ["python", "creative_uploader.py"]