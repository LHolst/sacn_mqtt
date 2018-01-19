import paho.mqtt.client as mqtt

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.subscribe("dmx/#", 0)
mqttc.loop_forever()