FROM python:3.11
LABEL creator="https://github.com/kalishevgeniy"

WORKDIR /var/lib/server
COPY . /var/lib/server
COPY ./main.py /var/lib/server

WORKDIR /var/lib/server/src
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /var/lib/server
