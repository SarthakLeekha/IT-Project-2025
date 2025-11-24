FROM nginx:alpine


COPY frontend.html /usr/share/nginx/html/index.html
COPY js/ /usr/share/nginx/html/js/


EXPOSE 80


CMD ["nginx", "-g", "daemon off;"]
