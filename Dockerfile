FROM python:3.6-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

COPY requirements.txt ./
COPY /docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x sacn_mqtt.py

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["pub"]
