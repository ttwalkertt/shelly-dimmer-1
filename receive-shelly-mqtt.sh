export MQTT_SERVER=localhost
export MQTT_PORT=1883
export SHELLY_ID="shellyplus010v"
mosquitto_sub -h ${MQTT_SERVER} -p ${MQTT_PORT} -t ${SHELLY_ID}/events/rpc

