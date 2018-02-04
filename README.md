# ECSE-428 Books4U
## Development setup:
1. install Docker [Download Docker](https://www.docker.com/community-edition#/download)
2. git clone this repo
3. cd into repo folder(the folder contains Dockerfile) and run:
```
    docker build -t books4u .
    docker run -p 80:80 books4u
```
the first command will download and install all dependencies 

the second command will start the server

4. go to [http://127.0.0.1/](http://127.0.0.1/) and you should see the main page (there isn't one as of 2018-2-4)
5. go to [http://127.0.0.1/admin](http://127.0.0.1/admin) and you should see the admin page, log in as 'admin' password: 'books4ubooks4u'here you can use the admin page to edit the database.

## Basics of development: 
1. Define api url in code/books4u/api.py
2. Write actual implementation of api in api.py (same folder)
3. Write unit tests in tests.py
3. Do NOT edit any other files.
