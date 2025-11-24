FROM nginx:alpine

# Copy frontend files to nginx html directory
COPY frontend.html /usr/share/nginx/html/index.html
COPY js/ /usr/share/nginx/html/js/
COPY tests/ /usr/share/nginx/html/tests/

# Copy custom nginx config if needed (optional)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
