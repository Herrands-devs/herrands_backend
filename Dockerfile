# Use an official base image for Python
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2 dependencies and other system packages
RUN apt-get update && \
    apt-get -y install gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the project files
COPY . .

# Run database migrations
RUN python manage.py migrate

# Set the PORT environment variable and use it in the CMD
ENV PORT 8000
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:$PORT"]