#!/usr/bin/env python
import sacn
import time
import paho.mqtt.client as mqtt
import logging
import signal
import sys
import os

logger = logging.getLogger('sacn_mqtt')
logger.setLevel(logging.DEBUG)


def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(r, g, b):
    return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

receiver = sacn.sACNreceiver()
mqttc = mqtt.Client()

@receiver.listen_on('universe', universe=1)  # listens on universe 1
def cb_universe(packet):  # packet type: sacn.DataPacket
    data = rgb_to_hex(*packet.dmxData[:3])
    topic = 'dmx/%s' % packet.universe
    mqttc.publish(topic, data);
    logger.debug('Topic: %s Data: %s', topic, data)

@receiver.listen_on('availability', universe=1)
def cb_availability(universe, changed):
    logger.info('Universe changed: u:%s c:%s', universe, changed)


def signal_handler(signum, frame):
    logger.info('Exiting')
    receiver.stop()
    mqttc.loop_stop()
    mqttc.disconnect()
    logging.debug("Exiting on signal %d", signum)
    sys.exit(signum)


def main():
    # Register signal handler
    mqttc.connect("localhost", 1883,60)

    logger.info('Start Receiver')
    receiver.start()  # start the receiving thread
    logger.info('Start Mqtt Client')
    mqttc.loop_start()
    logger.info('Running as PID:%s', str(os.getpid()))


    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()