import json
from collections import namedtuple

import paho.mqtt.client as mqtt

from cli import do_set


def dict_to_namedtuple(dic):
    Weather = namedtuple(
        "Weather",
        [
            "parameter",
            "value",
            "sensor",
            "timestamp",
            "wait",
            "url",
            "keyfile",
            "username",
        ],
    )
    return Weather(
        dic["parameter"],
        dic["value"],
        dic["sensor"],
        dic["timestamp"],
        None,
        None,
        None,
        "my_key",
    )


def on_message(client, userdata, message):
    data = json.loads(message.payload, encoding="utf-8")
    print("Received message: ", data)
    print("Blockchain result: ", do_set(dict_to_namedtuple(data)))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


if __name__ == "__main__":
    mqttBroker = "192.168.1.62"

    client = mqtt.Client("Node1")
    client.connect(mqttBroker)
    client.on_connect = on_connect
    client.subscribe("TEMPERATURE")
    client.subscribe("HUMIDITY")
    print("Listening...")
    client.on_message = on_message
    client.loop_forever()
