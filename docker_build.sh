docker build --network maragi_net --tag daveshap/text_sensor:latest .
docker run -p 6001:6001 --name text_sensor --network maragi_net daveshap/text_sensor:latest