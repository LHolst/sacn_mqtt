import sacn
import time
import paho.mqtt.publish as publish

def clamp(x):
    return max(0, min(x, 255))

def rgb_to_hex(r, g, b):
    return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))

# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=1)  # listens on universe 1
def cb_universe(packet):  # packet type: sacn.DataPacket
    data = rgb_to_hex(*packet.dmxData[:3])
    print(data)  # print the received DMX data
    publish.single("dmx/out",data, hostname="localhost")

@receiver.listen_on('availability', universe=1)
def cb_availability(universe, changed):
    print(universe, changed)

# optional: if you want to use multicast use this function with the universe as parameter
#receiver.join_multicast(1)

time.sleep(60)  # receive for 10 seconds
receiver.stop()