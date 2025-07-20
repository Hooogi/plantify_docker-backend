import mariadb
import os
import mqtt_client
import decimal
from decimal import Decimal

def save_message_to_db(topic, message, cursor):
    try:
        pot_mac = topic.split("/")[-1]

        cursor.execute("SELECT pot_id FROM plant_pot WHERE pot_mac = ?", (pot_mac,))
        result = cursor.fetchone()
        if result is None:
            print(f"Für die Mac {pot_mac} gibt es keinen zugehörigen angelegten Topf")
            return
        pot_id = result[0]

        values = message.split(";")
        try:
            temperature = Decimal(values[0])
            sunlight = int(values[1])
            air_humidity = Decimal(values[2])
            soil_moisture = Decimal(values[3])
        except (ValueError, decimal.InvalidOperation) as e:
            print(e)
            return

        sql = "INSERT INTO sensor_reading (pot_id, temperature, sunlight, air_humidity, soil_moisture) VALUES (?,?,?,?,?)"
        cursor.execute(sql, (pot_id, temperature, sunlight, air_humidity, soil_moisture))
    except mariadb.Error as e:
        print(e)

mqtt_broker = os.getenv('MQTT_BROKER')
message_client = mqtt_client.MqttClient(
    broker=mqtt_broker,
    client_id="message_handler",
    topic="sensor/+",
    qos=1,
    save_to_db_callback=save_message_to_db
)

message_client.start()