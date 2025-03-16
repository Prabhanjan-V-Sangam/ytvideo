# Use an official Python image
FROM python:3.10

# Set working directory inside container
WORKDIR /app

# Copy all files to container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run Flask with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
