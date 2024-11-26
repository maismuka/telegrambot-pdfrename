# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install git and necessary packages
RUN apt-get update && apt-get install -y git

# Clone the repository from GitHub
RUN git clone https://github.com/maismuka/telegrambot-pdfrename.git /app

# Install the Python dependencies
RUN pip install --no-cache-dir python-telegram-bot

# Make sure the volume directory exists and set appropriate permissions
RUN mkdir -p /volume1/audit_temp && chmod -R 777 /volume1/audit_temp

# Run the bot script
CMD ["python", "./audit.py"]
