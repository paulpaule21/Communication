#!/usr/bin/env python3
# Attention: Do not import the ev3dev.ev3 module in this file
from importlib.resources import path
import json
from pickle import NONE
import platform
import ssl
from tracemalloc import start
from paho.mqtt import client as mqtt_client
import logging
from types import SimpleNamespace
# Fix: SSL certificate problem on macOS
if all(platform.mac_ver()):
    from OpenSSL import SSL
class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """
    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        self.client.username_pw_set('012', password='ML9xxIRAKF') # these are our credentials for the connection with the motherboard
        self.client.connect('mothership.inf.tu-dresden.de', port=8883) # connection with the motherboard --> broker address and port 
        self.client.subscribe('explorer/012', qos=1) # subscripe to different channels/'topics' --> meaning planets & qos=1 --> receiver gets the message at least once
        self.client.on_connect = self.on_connect
        self.logger = logger
    # the function on_connect tells us whether the connection is established or not
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to Mothership!")
            message = '''{"from": "client", "type": "path", "payload": {"startX": -9,"startY": -2,"startDirection": 0,"endX": 10,"endY": 6,"endDirection": 90,"pathStatus": "free"}}'''
            # NOW:
            # 1st "type":"testplanet" --> set the planet on which we are  
            # 2nd "type":"ready" --> get the planet's information
            #
            #EXAM:
            # just "ready" because the mothership already knows where we are
            self.client.publish("planet/Chia/012", payload=message, qos=1)

        else:
            print("Failed to connect, return code %d\n", rc)   
    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.info(json.dumps(payload, indent=2))  
        print(json.dumps(payload, indent=2))
        self.receive_messages(message, payload)

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """  
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))
        #publish the message 
        self.client.publish("explorer/012", payload=message, qos=1)   
    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise     

    #def mothership_message_decoder():
    
    def receive_messages(self, message, payload):
        msg = NONE
        if payload["from"] == "server" and payload["type"] == "planet": 
            msg = "planet set"
            print("planet")
        elif payload["from"] == "server" and payload["type"] == "path": 
            msg = "path message"
            print("path")
        elif payload["from"] == "server" and payload["type"] == "pathSelect":
            msg = "path message"
            print("pathSelect")
        elif payload["from"] == "server" and payload["type"] == "pathUnveiled":
            msg = "path unveiled"
            print("pathUnveiled")
        elif payload["from"] == "server" and payload["type"] == "target":
            msg = "target sent"
            print("target")
        elif payload["from"] == "server" and payload["type"] == "done":
            msg = "we're done"
            print("done")
    

#path-message:
#(1) Publish to planet/<PLANET>/<GROUP>:
#'''{"from": "client", "type": "path", "payload": {"startX": <Xs>,"startY": <Ys>,"startDirection": <Ds>,"endX": <Xe>,"endY": <Ye>,"endDirection": <De>,"pathStatus": "free|blocked"}}'''
#pathSelect-message:
#(1) Publish to planet/<PLANET>/<GROUP>:
#'''{"from": "client", "type": "pathSelect", "payload": {"startX": <Xs>,"startY": <Ys>,"startDirection": <Ds>}}'''
#pathUnveiled-message:
#(1) Publish to planet/<PLANET>/<GROUP>:
#'''{"from": "client", "type": "targetReached", "payload": {"message": "<TEXT>"}}'''


def main():
    print("okay, let's go!")
    log = logging.getLogger("my-logger")
    client = mqtt_client.Client("012")
    ts = Communication(client, log)
    #client.loop_forever()
    client.loop_forever()
        

if __name__ == "__main__":
    main()

#def save_messages():
