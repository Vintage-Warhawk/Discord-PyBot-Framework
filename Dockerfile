# File: Dockerfile
# Maintainer: Vintage Warhawk
# Last Edit: 2025-11-17
#
# Description:
# This Dockerfile sets up a container environment for the Discord bot framework.
# It uses a lightweight Python 3.12 image, installs dependencies, and copies
# all project files into the container. The bot starts automatically when the
# container runs.

# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY pybot/ /app/pybot/

# Default command to run the bot
CMD ["python", "-u", "pybot/bot.py"]