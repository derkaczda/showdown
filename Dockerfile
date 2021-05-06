FROM pmariglia/gambit-docker as debian-with-gambit

FROM python:3.6-slim

COPY --from=debian-with-gambit /usr/local/bin/gambit-enummixed /usr/local/bin
COPY . /showdown 

WORKDIR /showdown

#COPY requirements.txt /showdown/requirements.txt

RUN pip3 install -r requirements.txt

RUN cp envs/.env .env

ENV PYTHONIOENCODING=utf-8
ENV GAMBIT_PATH=gambit-enummixed
EXPOSE 8081
CMD ["python3", "run.py"]
