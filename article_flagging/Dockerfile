FROM python:3.11-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y gcc libaio1 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]