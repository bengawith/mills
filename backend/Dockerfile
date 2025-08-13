# backend/Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set environment variables to prevent buffering and .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install dependencies
# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# 5. Copy your application code into the container
COPY . /app/

# 6. Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]