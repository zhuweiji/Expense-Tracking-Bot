# Use an official Python runtime as a parent image
FROM python:3.10.8-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app


# Define environment variable
# ENV NAME World

# Run bot.py when the container launches
CMD ["python", "-m", "main"]