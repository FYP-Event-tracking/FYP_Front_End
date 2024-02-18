# Use the official Python image as a base image
FROM python:3.9-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y install build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the app files into the container
COPY . .

# Expose the port streamlit will run on
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "--server.port", "8501", "app.py"]
