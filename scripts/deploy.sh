docker kill protocols_container
docker rm protocols_container

docker build -t protocols_image ..
docker run -d \
  --env MAIL_USERNAME --env MAIL_PASSWORD --env MAIL_SERVER --env MAIL_PORT --env MAIL_USE_TLS \
  --name protocols_container -p 8080:8080 protocols_image
# docker exec -it protocols_container bash
