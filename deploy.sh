git pull

# shut down all containers (remove images and volumes)
docker compose -f docker-compose.yml down --volumes --rmi local

# make sure images are removed
docker image rm -f glimepiride-app_backend:latest

# cleanup all dangling images, containers, volumes and networks
docker system prune --force

docker compose -f docker-compose.yml up --force-recreate --always-recreate-deps --build --detach
