FROM ubuntu:16.04

MAINTAINER ZishengWang

# Install required packages and remove the apt packages cache when done.

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	git \
	python3 \
	python3-pip
# install deps
RUN pip3 install django psycopg2


# add our code
COPY ./code /

EXPOSE 80
EXPOSE 5432

CMD ["python3","manage.py", "runserver", "0.0.0.0:80" ]