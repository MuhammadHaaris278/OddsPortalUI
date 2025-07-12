FROM python:3.13-slim

# Install dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstgl-1.0-0 \
    libgstcodecparsers-1.0-0 \
    libavif15 \
    libenchant2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2 \
    && apt-get clean

# Install your Python requirements
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Playwright install
RUN playwright install

# Set working directory
WORKDIR /app

# Run your app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
