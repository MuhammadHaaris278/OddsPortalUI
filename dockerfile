# Use a Python base image (slim version for smaller size)
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app

# Install system dependencies needed for Playwright to work
RUN apt-get update && \
    apt-get install -y \
    wget \
    ca-certificates \
    curl \
    libx11-dev \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libdbus-1-3 \
    libxtst6 \
    libnss3 \
    libxss1 \
    libxrandr2 \
    libgbm1 \
    libnss3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the postinstall.sh script executable and run it to install Playwright browsers
RUN chmod +x /app/postinstall.sh && /app/postinstall.sh

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
