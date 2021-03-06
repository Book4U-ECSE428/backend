# ECSE-428 Books4U
[![Build Status](https://travis-ci.org/Book4U-ECSE428/backend.svg?branch=master)](https://travis-ci.org/Book4U-ECSE428/backend)
## Deployment
1. Download books4u.pem cert from Google Drive
2. shh to aws ec2 instance
```
ssh -i "books4u.pem" ubuntu@ec2-35-182-205-51.ca-central-1.compute.amazonaws.com
```
3. run deploy.sh
```
sudo bash deploy.sh
```
## Development setup:
1. we need python 3.6 and pip
```
sudo apt-get install python3 python3-pip
```
2. install dependiencies
```
pip3 install django psycopg2 django-cors-headers
```
3. use your faviour IDE to write code
4. to start the server manually run:
```
python3 manage.py runserver
```
## admin page
127.0.0.1:8000/admin
```
user: admin
password: books4ubooks4u
```
## Testing setup:
1. install Docker [Download Docker](https://www.docker.com/community-edition#/download)
2. git clone this repo
3. cd into repo folder(the folder contains Dockerfile) and run:
```
docker build -t books4u .
docker run books4u
```
the first command will download and install all dependencies
the second command will start the test

## Basics of development:
1. Define api url in code/books4u/api.py
2. Write actual implementation of api in api.py (same folder)
3. Write unit tests in tests.py
3. Do NOT edit any other files.
