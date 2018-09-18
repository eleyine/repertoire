docker kill repertoire_container
docker rm repertoire_container

docker build -t repertoire_image ..

docker run -d  -v c:/Users/p0001073/Repertoire/repo/container/data:/data -e LISTEN_PORT=5001 --env-file secret_env_smtpchum.list --name repertoire_container -p 5001:5001 repertoire_image

# docker exec -it repertoire_container bash
