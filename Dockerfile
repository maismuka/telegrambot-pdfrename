# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git

# Clone the repository
RUN git clone https://github.com/maismuka/telegrambot-pdfrename.git /app

# Set default environment variables for scheduler time
ENV SCHEDULE_HOUR=15
ENV SCHEDULE_MINUTE=52

# Install required packages
RUN pip install --no-cache-dir python-telegram-bot

# Run the bot script
CMD ["python", "./audit.py"]
