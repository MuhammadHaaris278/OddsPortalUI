FROM python:3.13-slim

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    libx11-6 \
    libxcomposite1 \
    libxrandr2 \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libnss3 \
    libnspr4 \
    libxss1 \
    libgconf-2-4 \
    libgstreamer1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
RUN playwright install
RUN playwright install-deps

# 🔥 CRITICAL FIX: Copy all application code
COPY . .

# Expose the port that uvicorn will run on
EXPOSE 8000

# Health check to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the app with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
