# Use an official Python runtime as the base image
FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential gfortran gcc libopenblas-dev liblapack-dev libatlas-base-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*
# Set the working directory in the container
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt
RUN pip install pydantic[email]  
# Expose the port the app runs on
EXPOSE 8000
# Run the FastAPI application using uvicorn with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]