import json
import threading
import paho.mqtt.client as mqtt

# MQTT Broker Configuration
MQTT_BROKER = "localhost"  # Use "127.0.0.1" if needed
MQTT_PORT = 1883
MQTT_TOPIC = "zigbee2mqtt/Smart_Knob_1"

# Global state variables
brightness = 0
is_on = False  # Keeps track of on/off status
lock = threading.Lock()  # Ensures thread safety

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
            print(f"Status: {status} | Brightness: {brightness}")

    except json.JSONDecodeError:
        print("Error: Received invalid JSON payload.")

def on_connect(client, userdata, flags, rc):
    """
    Callback function triggered when connected to the MQTT broker.
    Subscribes to the relevant topic.
    """
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to {MQTT_TOPIC}")
    else:
        print(f"Connection failed with code {rc}")

def main():
    """
    Initializes and starts the MQTT client.
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_forever()  # Blocking loop to keep listening
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

