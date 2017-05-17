FROM python:3.6.1

MAINTAINER Spencer Krum <nibz@spencerkrum.com>

RUN git clone https://github.com/ibm-dev-incubator/starcraft-stacked-graph-service

EXPOSE 5000

RUN pip install -r starcraft-stacked-graph-service/requirements.txt


WORKDIR starcraft-stacked-graph-service

CMD python web.py

