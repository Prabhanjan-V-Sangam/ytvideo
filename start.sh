#!/bin/sh

# Start your Flask app in the background
python3 /app/app.py &

# Start OpenResty (Nginx + Lua) in foreground so container stays alive
exec /usr/local/openresty/bin/openresty -g "daemon off;"
