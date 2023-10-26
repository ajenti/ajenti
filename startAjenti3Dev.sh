#! /bin/bash

# Check if startFrontEnd.sh exists in the current directory
if [ ! -f startFrontEnd.sh ]; then
    echo "startFrontEnd.sh not found in the current directory. Exiting."
    exit 1
fi

DOCKER_IMAGE="maddi02/ajenti:0.0.1.RELEASE"
DOCKER_CONTAINER="aj3"

if [ -z "$(docker images -q $DOCKER_IMAGE)" ]; then
    echo "Image does not exist, pulling..."
    docker pull $DOCKER_IMAGE
else
    echo "Image exists, skipping pull..."
fi

if [ -n "$(docker ps -q -f name=$DOCKER_CONTAINER)" ]; then
    echo "Container is running, stopping and removing..."
    docker stop $DOCKER_CONTAINER
    docker rm $DOCKER_CONTAINER
else
    echo "Container is not running, skipping stop and remove..."
fi

source startFrontEnd.sh start








docker run -t -p 8000:8000 --name $DOCKER_CONTAINER $DOCKER_IMAGE