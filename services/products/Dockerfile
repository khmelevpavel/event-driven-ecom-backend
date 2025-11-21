FROM python:3.11-slim

WORKDIR /app

# Copy shared libraries first
COPY shared /app/shared

# Install shared dependencies
COPY shared/requirements.txt /tmp/shared-requirements.txt
RUN pip install --no-cache-dir -r /tmp/shared-requirements.txt || true

# Install service dependencies
COPY services/products/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/products /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

