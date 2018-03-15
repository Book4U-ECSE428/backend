#!/bin/bash
sudo docker swarm leave -f
git clone https://github.com/Book4U-ECSE428/front.git
mkdir ./code/ECSE428/static/
mv front/ ./code/ECSE428/static/
sudo docker build -t books4u-deploy -f Docker-deploy .
sudo docker swarm init
sudo docker stack deploy -c docker-compose.yml books4u-deploy
rm -rf ./code/ECSE428/static/
# docker swarm leave -f
