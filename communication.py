#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import platform
import ssl
import paho.mqtt.client as mqtt
from planet import Direction, Planet


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
        # Add your client setup here
        self.planetName = ""
        self.path = None
        self.pathWeight = None
        self.startX = None
        self.startY = None
        self.startOrientation = ""
        self.targetX = None
        self.targetY = None
        self.startDirection = ""
        self.logger = logger
        self.client.username_pw_set('015', password='H84xwwq7gk') # Your group credentials, see the python skill-test for your group password
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)
        self.client.subscribe('explorer/015', qos=2) # Subscribe to topic explorer/xxx

        self.client.loop_start()


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
        self.logger.debug(json.dumps(payload, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)
        print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic)

        # if payload["type"] == "planet":
        #  if "path" in payload.values():
        if payload["from"] == "server":

            if payload["type"] == "planet":
                planet_dict = payload.get("payload")

                self.planetName = str(planet_dict.get("planetName"))
                self.client.subscribe('planet/' + self.planetName + '/015', qos=2)

                #Alternartiv:
                # self.startX = payload["payload"]['startX']
                # self.startX = payload.payload.startX
                
                self.startX = planet_dict.get("startX")
                self.startY = planet_dict.get("startY")
                self.startOrientation = planet_dict.get("startOrientation")

                print(self.startOrientation, self.startX, self.startY)

            elif payload["type"] == "path":
                path_dict = payload.get("payload")

                if path_dict["pathStatus"] == "free":
                    self.pathWeight = path_dict.get("pathWeight")
    
                elif path_dict["pathStatus"] == "blocked":
                    self.pathWeight = -1 


            elif payload["type"] == "pathSelect":
                path_select_dict = payload.get("payload")
                self.startDirection = str(path_select_dict.get("startDirection"))
                print(self.startDirection)

            elif payload["type"] == "pathUnveiled":
                ## new_path muss zu vorhandenen Wegen hinzugefügt werden
                new_path = payload.get("payload")
                # self.startX = payload["payload"]['startX']
                # self.startX = payload.payload.startX

            elif payload["type"] == "target":
                target_dict = payload.get("payload")
                self.targetX = target_dict.get("targetX")
                self.targetY = target_dict.get("targetY")

            elif payload["type"] == "done":
                pass


        print("\n")

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

        # YOUR CODE FOLLOWS (remove pass, please!)
        #self.client.publish(topic, message, qos=2)
        self.client.publish(topic, json.dumps(message, indent=2), qos=2)

    def send_ready(self):
        topic = "explorer/015"
        rdy_msg = {"from": "client", "type": "ready"}

        self.send_message(topic, rdy_msg)

    #Darf nicht während der Prüfung gesendet werden.
    def send_test_planet(self):
        topic = "explorer/015"
        test_plnt_msg = {"from": "client", "type": "testplanet", "payload": { "planetName": "Chadwick"}}

        self.send_message(topic, test_plnt_msg)

    def send_path_msg(self):
        topic = 'planet/' + self.planetName + '/015'
        path_msg = {
        "from": "client",
        "type": "path",
        "payload": {
            "startX": self.startX,
            "startY": self.startY,
            "startDirection": self.startOrientation,
            "endX": 24,
            "endY": 44,
            "endDirection": Direction.NORTH,
            "pathStatus": "free"
                }
            }

        self.send_message(topic, path_msg)

    def send_path_select_msg(self):
        topic = 'planet/' + self.planetName + '/015'
        path_select_msg = {
        "from": "client",
        "type": "pathSelect",
        "payload": {
            "startX": 23,
            "startY": 3,
            "startDirection": Direction.NORTH
                }
            }
        
        self.send_message(topic, path_select_msg)


    def send_target_reached(self):

        topic = "explorer/015"
        target_reached_msg = {
        "from": "client",
        "type": "targetReached",
        "payload": {
            "message": "<TEXT>"
            }
        }
        self.send_message(topic, target_reached_msg)

    def send_explorationCompleted(self):

        topic = "explorer/015"
        expCom_msg = {
        "from": "client",
        "type": "explorationCompleted",
        "payload": {
            "message": "<TEXT>"
            }
        }

        self.client.subscribe('explorer/015', qos=2)
        
        self.send_message(topic, expCom_msg)

    
        

       
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
