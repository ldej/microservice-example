FROM python:3.5

ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install -e .

RUN cd ./microservice
RUN pip install -e .

RUN cd /code

CMD python ./app/main.py
