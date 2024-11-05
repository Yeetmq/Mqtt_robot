import os
import paho.mqtt.client as mqtt
from typing import Callable
from loguru import logger

logs_path = os.getenv("LOGS_PATH")
logs_path += "base_mqtt.log".replace('//', '/')
logger.add(sink=logs_path, format="{level} {time} {message}", level="DEBUG")

mqtt_broker = os.getenv("EMQX_HOST")
mqtt_port = os.getenv("MQTT_PORT")
mqtt_client_id = os.getenv("MQTT_CLIENTID")


class MQTTBase:
    global mqtt_broker, mqtt_port, mqtt_client_id

    def __init__(self, client_id: str = mqtt_client_id, broker: str = mqtt_broker, port: int = mqtt_port):
        self.broker: str = broker
        self.port: int = port

        self.client_id: str = client_id

        self.client: mqtt.Client or None = None
        self.topics: list[str] = []

        self._connect_mqtt()

    @logger.catch
    def _connect_mqtt(self) -> None:
        if isinstance(self.client, type(None)):
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.client_id)
            self.client.on_connect = MQTTBase.on_connect
            self.client.connect(self.broker, self.port)

    @logger.catch
    def send_message(self, topic: str, message: str) -> None:
        result = self.client.publish(topic, message)
        if result[0] == 0:
            logger.info(f"Send `{message}` to topic `{topic}`")
        else:
            logger.error(f"Failed to send message to topic {topic}")

    @logger.catch
    def subscribe(self, topic: str, callback_on_message: Callable) -> str:
        self.client.subscribe(topic)
        self.client.on_message = callback_on_message
        logger.info(f"Client subscribed to topic: {topic}")
        return topic

    @staticmethod
    def on_connect(client, userdata, flags, rc) -> None:
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error("Failed to connect, return code %d\n", rc)

    @logger.catch
    def _on_mqtt_message(self, client, userdata, msg) -> None:
        logger.info(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    @logger.catch
    def disconnect(self) -> None:
        if self.client:
            self.client.disconnect()
        else:
            logger.error("Attempt of repeat disconnect")