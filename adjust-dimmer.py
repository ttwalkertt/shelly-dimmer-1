import paho.mqtt.client as mqtt
import logging
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT broker details
broker = 'publicweb.local'
port = 1883
topic = 'shellyplus010v/rpc'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT Broker!")
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    logging.info(f"Message published (mid: {mid})")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.error(f"Unexpected disconnection. Return code: {rc}")
    else:
        logging.info("Disconnected from MQTT Broker")

# Create a new MQTT client instance
client = mqtt.Client()

# Assign event callbacks
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

try:
    # Connect to the broker
    client.connect(broker, port, 60)
    client.loop_start()  # Start the loop

    on_value = True
    while True:
        # Create the payload with the current on_value
        payload = f'{{"id":124, "src":"timtw", "method":"Light.Set", "params":{{"id":0,"on":{str(on_value).lower()}}}}}'
        #payload = '{"id": 1, "src":"timtw", "method": "Light.GetStatus", "params": {"id": 0}}'
        # Publish the payload to the topic
        print(f"Publishing message: {payload}")
        result = client.publish(topic, payload)
        # Check if the publish was successful
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logging.error(f"Failed to publish message: {result.rc}")
        # Toggle the on_value
        on_value = not on_value
        # Wait for 3 seconds before sending the next message
        time.sleep(3)

except Exception as e:
    logging.error(f"An error occurred: {e}")
finally:
    client.loop_stop()  # Stop the loop
    client.disconnect()