# Use the official Python image as the base image
FROM python:latest

# Install the required packages using pip
RUN pip install --no-cache-dir openai portkey-ai

# Set working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set the entrypoint to the script
ENTRYPOINT ["./entrypoint.sh"]
