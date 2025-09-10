FROM python:3.13.7-slim

# Set workdir
WORKDIR /app

# Install system dependencies for WeasyPrint and PDF rendering
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libxml2 libxslt1.1 libjpeg-dev zlib1g-dev unzip curl && \
    rm -rf /var/lib/apt/lists/*


# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Copy .env for API key and other secrets
COPY .env .env

# Expose the port Reflex will run on
EXPOSE 3000
EXPOSE 8000

# Set environment variables (optional, for production)
ENV PYTHONUNBUFFERED=1

# Run Reflex app
CMD ["reflex", "run"]
