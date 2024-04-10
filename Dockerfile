FROM python:3.8-alpine

WORKDIR /udp_server

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /udp_server
ENV MONGO_HOST=172.17.0.1 
EXPOSE 8081

CMD [ "python3", "udp_server.py"]