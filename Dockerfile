FROM python:3.8-buster

WORKDIR /srv/postman
COPY ./postman.py ./postman.py
COPY ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

CMD ["python3", "/srv/postman/postman.py"]
