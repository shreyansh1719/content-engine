FROM python:3.12-slim

WORKDIR /app

# System deps for Pillow, OpenCV, and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create runtime directories
RUN mkdir -p output/images/base output/images/final output/images/products \
    output/images/enhanced output/images/backgrounds output/images/composites \
    output/data output/excel logs data/feedback

EXPOSE 8000 8501

# Default: start both API and Streamlit
CMD ["bash", "-c", "uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run frontend_app.py --server.port 8501 --server.address 0.0.0.0"]
