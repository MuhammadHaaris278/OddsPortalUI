# Use the official Python image as the base
FROM python:3.13-slim

# Install required system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstgl-1.0-0 \
    libgstcodecparsers-1.0-0 \
    libavif15 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libglesv2-2.0 \
    wget \
    ca-certificates \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright's dependencies
RUN pip install --upgrade pip
RUN pip install playwright

# Install browsers required by Playwright
RUN playwright install

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port your app will run on
EXPOSE 8000

# Run the application with Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
