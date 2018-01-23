import os
import paho.mqtt.client as mqtt

TOPIC = os.getenv('MCLIGHTING_MQTT_TOPIC','ESP8266_01/#')
MQTT_HOST = os.getenv('MQTT_HOST','localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.subscribe(TOPIC, 0)
mqttc.loop_forever()