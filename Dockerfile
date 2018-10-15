FROM ubuntu

RUN apt-get update && apt-get install -y \
  python3 \
  python3-pika \
  python3-flask

ADD text_sensor.py /

CMD [ "python3", "./text_sensor.py" ]