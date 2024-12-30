# Use the official Python image as the base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install `wait-for-it` script
RUN curl -o /usr/local/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /usr/src/app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django app code
COPY ./app /usr/src/app

# Copy the Scrapy project code
COPY ./scraper /usr/src/scraper

# Expose Django port
EXPOSE 8000

# Run based on the service type
CMD ["sh", "-c", "if [ \"$SERVICE\" = 'django' ]; then wait-for-it db:5432 -- python manage.py migrate && python manage.py runserver 0.0.0.0:8000; elif [ \"$SERVICE\" = 'scrapy' ]; then scrapy crawl async_trip; else echo 'Invalid service specified'; fi"]
