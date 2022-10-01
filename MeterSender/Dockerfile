FROM python:3.10
RUN apt-get update && apt-get install -y locales
RUN sed -i -e \
  's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
   && locale-gen

ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

RUN pip install --upgrade pip

RUN mkdir -p /app
WORKDIR /app

COPY ./Docker/config.py ./MeterSender/config.py

COPY ./MeterSender/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./MeterSender/ ./MeterSender/

CMD ["python", "MeterSender/mr_sanding.py"]

