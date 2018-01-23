#!/usr/bin/env python
import sacn
import time
import paho.mqtt.client as mqtt
import logging
import signal
import sys
import os

logger = logging.getLogger('sacn_mqtt')
logger.setLevel(logging.INFO)
TOPIC = os.getenv('MCLIGHTING_MQTT_TOPIC','ESP8266_01/in')
TOPIC_OUT = os.getenv('MCLIGHTING_MQTT_TOPIC_OUT',TOPIC.replace('/in','/out'))
MQTT_HOST = os.getenv('MQTT_HOST','localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))



def clamp(x):
    return max(0, min(x, 255))

def rgbToHex(r, g, b):
    return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

def getRange(start, end):
    return f'R{start:02d}{end:02d}'

def getSingle(num):
    return f'+{num:02d}'

def getRgb(packet, index):
    return packet.dmxData[index*3:index*3+3]


def dmxToMqtt(packet):
    logger.debug(packet.dmxData[:16])
    #data = "*"+rgbToHex(*packet.dmxData[:3])
    #data = getRange(0,3)+rgbToHex(*getRgb(packet,0))
    #data += getRange(4,7)+rgbToHex(*getRgb(packet,1))
    data = getSingle(0)+rgbToHex(*getRgb(packet,0))
    data += getSingle(1)+rgbToHex(*getRgb(packet,1))
    data += getSingle(2)+rgbToHex(*getRgb(packet,0))
    data += getSingle(3)+rgbToHex(*getRgb(packet,1))
    data += getSingle(4)+rgbToHex(*getRgb(packet,0))
    data += getSingle(5)+rgbToHex(*getRgb(packet,1))
    data += getSingle(6)+rgbToHex(*getRgb(packet,0))
    data += getSingle(7)+rgbToHex(*getRgb(packet,1))
    return data

receiver = sacn.sACNreceiver()
mqttc = mqtt.Client()
current_milli_time = lambda: int(round(time.time() * 1000))
last_time = current_milli_time()
wait_for_ok = False
@receiver.listen_on('universe', universe=1)  # listens on universe 1
def cb_universe(packet):  # packet type: sacn.DataPacket
    global wait_for_ok
    global last_time
    logger.debug(f'cb universe wait:{wait_for_ok}')
    if not wait_for_ok:
        wait_for_ok = True
        last_time = current_milli_time()
        data = dmxToMqtt(packet)
        topic = TOPIC
        mqttc.publish(topic, data, qos=0, retain=False);
        logger.debug('Topic: %s Data: %s', topic, data)

@receiver.listen_on('availability', universe=1)
def cb_availability(universe, changed):
    logger.info('Universe changed: u:%s c:%s', universe, changed)

def on_message(mqttc, obj, msg):
    global wait_for_ok
    logger.debug(f'on on_message wait:{wait_for_ok}')
    logger.debug(f'{msg.topic} {msg.qos} {msg.payload}')
    #logger.info(f'first byte:{msg.payload[0]}')
    if msg.payload[0] == ord('O'):
        logger.info(f'latency: {current_milli_time()-last_time}')
        wait_for_ok = False


def signal_handler(signum, frame):
    logger.info('Exiting')
    receiver.stop()
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)


def main():
    # Register signal handler
    mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
    mqttc.on_message = on_message
    mqttc.subscribe(TOPIC_OUT, 0)


    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

    logger.info('Start Receiver')
    receiver.start()  # start the receiving thread
    logger.info('Start Mqtt Client')
    mqttc.loop_start()
    logger.info('Running as PID:%s', str(os.getpid()))


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()