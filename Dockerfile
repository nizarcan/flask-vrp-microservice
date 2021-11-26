FROM python:3.8
ADD . /flask-vrp-microservice
WORKDIR /flask-vrp-microservice
RUN pip install -r requirements.txt