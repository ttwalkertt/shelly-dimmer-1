import json
import paho.mqtt.client as mqtt
import logging
import os
import threading

# MQTT Connection
MQTT_BROKER = "publicweb.local"  # Change this to your MQTT broker address
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = "zigbee2mqtt/Smart_Knob_1"

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Remove default handler to avoid duplicate log entries
if logger.hasHandlers():
    logger.handlers.clear()

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('smart_knob_mqtt.log')

# Set level for handlers
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Constants
DEFAULT_ACTION_STEP_SIZE = 10
MAX_BRIGHTNESS = 100
MIN_BRIGHTNESS = 0
LOG_FILE_PATH = 'smart_knob_log.txt'
MAX_LOG_LINES = 1000
TRUNCATE_INTERVAL = 1000
LOCK_TIMEOUT = 2  # Timeout in seconds for acquiring the lock

# Message counter
message_counter = 0

def truncate_log_file():
    """Truncates the log file if it exceeds a certain number of lines."""
    try:
        with open(LOG_FILE_PATH, 'r') as file:
            lines = file.readlines()
        if len(lines) > MAX_LOG_LINES:
            with open(LOG_FILE_PATH, 'w') as file:
                file.writelines(lines[-MAX_LOG_LINES:])
            logging.info(f"Truncated log file to the last {MAX_LOG_LINES} lines.")
    except Exception as e:
        logging.error(f"Error truncating log file: {e}")

class SmartKnobParser:
    def __init__(self):
        """Initializes the SmartKnobParser."""
        logging.debug("SmartKnobParser initialized")
        self._brightness = 0
        self._output = False
        self._dirty = False
        self._lock = threading.Condition()

    @property
    def brightness(self):
        """Gets the current brightness value."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                return self._brightness
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for brightness")

    @brightness.setter
    def brightness(self, value):
        """Sets the brightness value and marks the state as dirty."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                self._brightness = value
                self._dirty = True  # Set _dirty directly to avoid deadlock
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for setting brightness")

    @property
    def output(self):
        """Gets the current output state."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                return self._output
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for output")

    @output.setter
    def output(self, value):
        """Sets the output state and marks the state as dirty."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                self._output = value
                self._dirty = True  # Set _dirty directly to avoid deadlock
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for setting output")

    @property
    def dirty(self):
        """Gets the dirty state."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                return self._dirty
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for dirty")

    @dirty.setter
    def dirty(self, value):
        """Sets the dirty state."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                self._dirty = value
            finally:
                self._lock.release()
        else:
            raise TimeoutError("Failed to acquire lock for setting dirty")

    def parse_message(self, topic: str, payload: str):
        """
        Parses an MQTT message, extracts its fields, and processes it accordingly.
        
        :param topic: The MQTT topic (not used in logic but included for completeness).
        :param payload: The JSON-formatted payload string.
        :return: None
        """
        logging.debug(f"Parsing message from topic: {topic} with payload: {payload}")
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            logging.error("Invalid JSON payload")
            return

        operation_mode = data.get("operation_mode")
        action = data.get("action")

        if operation_mode == "command":
            self.handle_command(action, data)
        elif operation_mode == "event":
            self.handle_event(action, data)
        else:
            logging.error(f"Unknown operation mode: {operation_mode}")

    def handle_command(self, action, data):
        """
        Handles 'command' operation mode actions.
        
        :param action: The action to be performed.
        :param data: The data associated with the action.
        :return: None
        """
        logging.debug(f"Handling command action: {action}")
        if action == "brightness_step_up":
            self.brightness_step_up(data)
        elif action == "brightness_step_down":
            self.brightness_step_down(data)
        elif action == "color_temperature_step_up":
            self.color_temperature_step_up(data)
        elif action == "color_temperature_step_down":
            self.color_temperature_step_down(data)
        elif action == "toggle":
            self.toggle(data)
        else:
            logging.error(f"Unhandled command action: {action}")

    def handle_event(self, action, data):
        """
        Handles 'event' operation mode actions.
        
        :param action: The action to be performed.
        :param data: The data associated with the action.
        :return: None
        """
        logging.debug(f"Handling event action: {action}")
        if action == "rotate_left":
            self.rotate_left(data)
        elif action == "rotate_right":
            self.rotate_right(data)
        elif action == "double":
            self.double_press(data)
        elif action == "single":
            self.single_press(data)
        else:
            logging.error(f"Unhandled event action: {action}")

    def brightness_step_up(self, data):
        """Increases brightness by the specified step size."""
        step_size = data.get('action_step_size', 0)
        self.brightness = min(MAX_BRIGHTNESS, self.brightness + step_size)
        logging.info(f"Increasing brightness by {step_size}. New brightness: {self.brightness}")

    def brightness_step_down(self, data):
        """Decreases brightness by the specified step size."""
        step_size = data.get('action_step_size', 0)
        self.brightness = max(MIN_BRIGHTNESS, self.brightness - step_size)
        logging.info(f"Decreasing brightness by {step_size}. New brightness: {self.brightness}")

    def color_temperature_step_up(self, data):
        """Increases color temperature by the specified step size."""
        logging.info(f"Increasing color temperature by {data.get('action_step_size', 0)}")

    def color_temperature_step_down(self, data):
        """Decreases color temperature by the specified step size."""
        logging.info(f"Decreasing color temperature by {data.get('action_step_size', 0)}")

    def toggle(self, data):
        """Toggles the state."""
        self.output = not self.output  # This calls the output setter
        logging.info(f"Toggling state. New output: {self.output}")

    def rotate_left(self, data):
        """Handles the rotate left action."""
        step_size = data.get('action_step_size', DEFAULT_ACTION_STEP_SIZE)
        self.brightness = max(MIN_BRIGHTNESS, self.brightness - step_size)
        logging.info(f"Knob rotated left by {step_size}. New brightness: {self.brightness}")

    def rotate_right(self, data):
        """Handles the rotate right action."""
        step_size = data.get('action_step_size', DEFAULT_ACTION_STEP_SIZE)
        self.brightness = min(MAX_BRIGHTNESS, self.brightness + step_size)
        logging.info(f"Knob rotated right by {step_size}. New brightness: {self.brightness}")

    def double_press(self, data):
        """Handles the double press action."""
        logging.info("Double press detected")

    def single_press(self, data):
        """Handles the single press action."""
        self.output = not self.output  # This calls the output setter
        logging.info(f"Single press detected. New output: {self.output}")

    def report_state(self):
        """Reports the current brightness and output state and clears the dirty flag."""
        if self._lock.acquire(timeout=LOCK_TIMEOUT):
            try:
                state = {
                    "brightness": self._brightness,
                    "output": self._output
                }
                self.dirty = False
            finally:
                self._lock.release()
            logging.info(f"Reporting state: {state}")
            return state
        else:
            raise TimeoutError("Failed to acquire lock for reporting state")

parser = SmartKnobParser()

def on_connect(client, userdata, flags, rc):
    """
    Callback for when the client receives a CONNACK response from the broker.
    
    :param client: The MQTT client instance.
    :param userdata: The private user data as set in Client() or userdata_set().
    :param flags: Response flags sent by the broker.
    :param rc: The connection result.
    :return: None
    """
    if rc == 0:
        logging.info("Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """
    Callback for when a PUBLISH message is received from the broker.
    
    :param client: The MQTT client instance.
    :param userdata: The private user data as set in Client() or userdata_set().
    :param msg: An instance of MQTTMessage.
    :return: None
    """
    global message_counter
    payload = msg.payload.decode("utf-8")
    logging.debug(f"Received message on topic: {msg.topic} with payload: {payload}")
    parser.parse_message(msg.topic, payload)
    message_counter += 1
    if message_counter >= TRUNCATE_INTERVAL:
        truncate_log_file()
        message_counter = 0

# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Blocking loop to process network traffic and dispatch callbacks
client.loop_forever()