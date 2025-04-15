
# Use Nginx as a lightweight web server
FROM nginx:alpine

# Remove the default Nginx index.html
RUN rm -rf /usr/share/nginx/html/*

# Copy all files from /Downloads/my-webpage to the Nginx HTML directory
COPY . /usr/share/nginx/html/
# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

