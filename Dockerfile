# Dockerfile cho Railway/Render deploy
# Override Nixpacks default vì src-layout không build wheel được trong sandbox

FROM python:3.11-slim

# System deps tối thiểu (build tools cho 1 số lib Python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements trước để cache layer tốt hơn (nếu code đổi mà deps không đổi → skip pip install)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code (flat layout — tiktok_insight_miner ở root)
COPY . .

# Streamlit settings
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Start command — exec form với sh -c để đảm bảo $PORT expand đúng
# Railway/Render tự inject $PORT env var khi container chạy
CMD ["/bin/sh", "-c", "streamlit run webapp.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true --server.enableCORS false --server.enableXsrfProtection false --browser.gatherUsageStats false"]
