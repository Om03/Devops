FROM ubuntu
RUN apt-get update -y && \ 
    apt-get install -y python3-pip python-dev

RUN mkdir app

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]
