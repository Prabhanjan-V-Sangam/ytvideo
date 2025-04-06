# Use the official Nginx image
FROM nginx:alpine

# Install Python, virtualenv, and dependencies
RUN apk add --no-cache python3 py3-pip py3-virtualenv

# Set the working directory
WORKDIR /app

# Copy application files
COPY app.py redispython.py /app/
#COPY app.py /app/app.py
COPY templates /app/templates
COPY requirements.txt /app/requirements.txt

# Create a virtual environment and install dependencies inside it
RUN python3 -m venv /app/venv && \
    . /app/venv/bin/activate && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Create cache folder for Nginx and set permissions
RUN mkdir -p /var/cache/nginx/video_cache && chmod -R 777 /var/cache/nginx/video_cache

# Expose Flask (5000) and Nginx (8081) ports
EXPOSE 5000 8081

# Start both Flask and Nginx
#CMD ["sh", "-c", "nginx && . /app/venv/bin/activate && python /app/app.py & /app/pythonlogwatcher.py"]
CMD ["sh", "-c", "/app/venv/bin/python /app/app.py & /app/venv/bin/python /app/redispython.py & nginx -g 'daemon off;'"]
