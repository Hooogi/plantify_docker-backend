import mqtt_client
import os

mqtt_broker = os.getenv('MQTT_BROKER')
registration_client = mqtt_client.MqttClient(
    broker=mqtt_broker,
    client_id="registration_handler",
    topic="plant_pot",
    qos=1,
)

registration_client.start()