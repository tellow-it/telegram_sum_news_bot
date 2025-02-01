ARG BASE_IMAGE=python:3.12
FROM $BASE_IMAGE


# download utils
RUN apt-get -y update && \
    apt-get install libpq-dev -y && \
    apt-get install libgl1-mesa-glx -y

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .

# pip & requirements
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY . .
