# Use official Python 3.13 image as base
FROM python:3.13-slim

# Install system dependencies
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
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install pip dependencies
RUN pip install --upgrade pip
RUN pip install playwright

# Install the required browsers
RUN playwright install

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the project files
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
