#!/bin/bash
# git stash
# git checkout master
# git pull
sudo docker swarm leave -f
sudo service docker stop
sudo service docker start
git clone https://github.com/Book4U-ECSE428/front.git
mkdir ./code/ECSE428/static/
mv front/ ./code/ECSE428/static/
sudo docker build -t books4u-deploy -f Docker-deploy .
# sudo docker run -d -p 80:80 -p 8080:8080 -p 8000:8000 books4u-deploy
sudo docker swarm init
sudo docker stack deploy -c docker-compose.yml books4u-deploy
rm -rf ./code/ECSE428/static/
