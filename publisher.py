import json
import paho.mqtt.client as mqtt
import sys
import time
import board
from datetime import datetime
import adafruit_dht
#from weather_app.cli import do_set

def make_payload(parameter, value, sensor, timestamp):
    data = {"parameter": parameter, "value": value, "sensor": sensor, "timestamp": timestamp}
    return json.dumps(data).encode("utf-8")

if __name__ == "__main__":
    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT22(board.D4)
    sensor = 'sensor_1' if len(sys.argv) < 2 else sys.argv[1]

    mqttBroker = "localhost"
    client = mqtt.Client(sensor)
    client.connect(mqttBroker)

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

    while True:
        try:
            # Print the values to the serial port
            timestamp = datetime.now().isoformat('T', 'seconds')
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            client.publish('TEMPERATURE', make_payload('temperature', temperature_c, sensor, timestamp))
            client.publish('HUMIDITY', make_payload('humidity', humidity, sensor, timestamp))
            print("Message published")
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
        except KeyboardInterrupt:
            print("Stop sensor reading...")
            dhtDevice.exit()

        time.sleep(5.0)
    
    

