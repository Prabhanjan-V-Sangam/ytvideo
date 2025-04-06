# Use the official Nginx image
FROM openresty/openresty:alpine

# Install Python, virtualenv, and dependencies
RUN apk add --no-cache python3 py3-pip curl unzip git make

# Set the working directory
WORKDIR /app

# Install lua-resty-redis manually
RUN mkdir -p /usr/local/openresty/nginx/lua
RUN git clone https://github.com/openresty/lua-resty-redis.git /app/lua-resty-redis \
    && mkdir -p /usr/local/openresty/lualib/resty \
    && cp /app/lua-resty-redis/lib/resty/redis.lua /usr/local/openresty/lualib/resty/
RUN git clone https://github.com/openresty/lua-resty-core.git /tmp/lua-resty-core
RUN cd /tmp/lua-resty-core && make install LUA_LIB_DIR=/usr/local/openresty/lualib
RUN rm -rf /tmp/lua-resty-core
# Copy application files
COPY app.py /app/app.py
COPY templates /app/templates
COPY requirements.txt /app/requirements.txt
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY lua /usr/local/openresty/nginx/lua
COPY start.sh /start.sh
# Create a virtual environment and install dependencies inside it
RUN pip install --break-system-packages -r /app/requirements.txt
RUN chmod +x /start.sh
# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Create cache folder for Nginx and set permissions
RUN mkdir -p /var/cache/nginx/video_cache && chmod -R 777 /var/cache/nginx/video_cache

# Expose Flask (5000) and Nginx (8081) ports
EXPOSE 5000 8081

# Start both Flask and Nginx
#CMD ["sh", "-c", "nginx &&  python /app/app.py"]
CMD ["/start.sh"]
#. /app/venv/bin/activate && line 17  . /app/venv/bin/activate && \ line 16 python3 -m venv /app/venv && \  py3-virtualenv   --no-cache-dir -r