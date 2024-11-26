# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/maismuka/telegrambot-pdfrename.git /app

# Pull the latest changes from GitHub whenever you rebuild
RUN cd /app && git pull origin main

# Install the specific version of python-telegram-bot
RUN pip install --no-cache-dir python-telegram-bot==20.0

# Set default environment variables for scheduler time
ENV SCHEDULE_HOUR=23
ENV SCHEDULE_MINUTE=50

# Run the bot script
CMD ["python", "./audit.py"]
