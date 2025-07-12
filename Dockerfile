FROM python:3.13-slim

# Install general dependencies required by Playwright and your app
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
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Install Playwright dependencies
RUN playwright install

# Set working directory
WORKDIR /app

# Run the app with uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
