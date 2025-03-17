FROM nginx:alpine

# Copy main Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy server configuration
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
