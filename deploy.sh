#!/bin/bash
git clone https://github.com/Book4U-ECSE428/front.git
mv front/ ./code/ECSE428/static/
rm -rf front/
sudo docker build -t books4u-deploy -f Docker-deploy .
sudo docker swarm init
sudo docker stack deploy -c docker-compose.yml books4u-deploy
# docker swarm leave -f
