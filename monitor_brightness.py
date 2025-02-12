import json
import threading
import paho.mqtt.client as mqtt
import logging

# MQTT Broker Configuration
MQTT_BROKER = "localhost"  # Use "127.0.0.1" if needed
MQTT_BROKER = "publicweb.local"
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/Smart_Knob_1"

# Global state variables
brightness = 0
is_on = False  # Keeps track of on/off status
lock = threading.Lock()  # Ensures thread safety

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
mqtt_logger = logging.getLogger("paho.mqtt.client")
mqtt_logger.setLevel(logging.DEBUG)

def on_subscribe(client, userdata, mid, reason_codes, properties):
    for sub_result in reason_codes:
        if sub_result == 1:
            # process QoS == 1
        # Any reason code >= 128 is a failure.
            pass    
        if sub_result >= 128:
            # error processing
            pass

def on_message(client, userdata, msg):
    """
    Callback function triggered when an MQTT message is received.
    Parses the JSON payload and updates brightness or power state.
    """
    try:
        payload = json.loads(msg.payload.decode())  # Convert message to dictionary

        with lock:
            global brightness, is_on

            if payload.get("action") == "brightness_step_up":
                brightness += payload.get("action_step_size", 0)
                brightness = min(255, brightness)  # Clamp to 255 max

            elif payload.get("action") == "brightness_step_down":
                brightness -= payload.get("action_step_size", 0)
                brightness = max(0, brightness)  # Clamp to 0 min

            elif payload.get("action") == "toggle":
                is_on = not is_on  # Toggle the on/off state
                if (is_on) and brightness < 127: brightness = 127

            # Display the current status
            status = "ON" if is_on else "OFF"
            logging.info(f"Topic: {msg.topic} | Status: {status} | Brightness: {brightness}")

    except json.JSONDecodeError:
        logging.error("Error: Received invalid JSON payload.")

def on_connect(client, userdata, flags, reason_code, properties):
    """
    Callback function triggered when connected to the MQTT broker.
    Subscribes to the relevant topic.
    """
    if reason_code == 0:
        logging.info("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        logging.info(f"Subscribed to {MQTT_TOPIC}")
    else:
        logging.error(f"Connection failed with code {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    """
    Callback function triggered when disconnected from the MQTT broker.
    """
    logging.info(f"Disconnected from MQTT Broker with code {reason_code}")

def main():
    """
    Initializes and starts the MQTT client.
    """
    client = mqtt.Client(protocol=mqtt.MQTTv5)  # Use MQTT version 5
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()  # Blocking loop to keep listening
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    logging.info("Starting Monitor Brightness Controller...")
    main()