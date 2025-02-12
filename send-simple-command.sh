export MQTT_SERVER="publicweb.local"
export MQTT_PORT=1883
export SHELLY_ID="shellyplus010v" # The <shelly-id> of your device
mosquitto_pub -h ${MQTT_SERVER} -p ${MQTT_PORT} -t ${SHELLY_ID}/command -m status_update
