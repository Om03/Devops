FROM ubuntu
RUN apt-get update -y && \ 
    apt-get install -y python3-pip python-dev

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
