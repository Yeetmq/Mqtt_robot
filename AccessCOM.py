import json
import os

from loguru import logger
from threading import Thread
from datetime import datetime
from typing import Any

from utils.BaseCOM import COMBase
from utils.BaseMqtt import MQTTBase
from Devices import IS, US, RFID, BATTERY, CameraServo, Wheels, Flashlight, UVFlashlight


logs_path = os.getenv("LOGS_PATH")
logs_path += "base_hardware.log".replace('//', '/')
logger.add(sink=logs_path, format="{level} {time} {message}", level="ERROR")


class BaseSerialToMQTTConnector(MQTTBase, COMBase):
    def __init__(self,
                 serial_path: str,
                 baudrate: int, timeout: int,
                 broker: str, port: int,
                 root_topic: str, command_topic: str,
                 mqtt_msg_split_sym: str):

        COMBase.__init__(self, serial_path=serial_path, baudrate=baudrate, timeout=timeout)
        MQTTBase.__init__(self, broker=broker, port=port)

        self.mqtt_msg_split_sym = mqtt_msg_split_sym
        self.root_topic: str = root_topic
        self.command_topic: str = command_topic
        self.subscribed_topic = self.subscribe(f"{self.root_topic}/{self.command_topic}".replace('//', '/'),
                                               self._on_mqtt_message)

        self.threading_read = Thread(target=self.read_from_serial_loop, daemon=True)
        self.threading_listen_mqtt = Thread(target=self.client.loop_forever, daemon=True)

    @logger.catch
    def start(self):
        self.threading_read.start()
        self.threading_listen_mqtt.start()

        logger.info(f"Work with the {self.serial_path} has begun")

    @logger.catch
    def close(self) -> None:
        if self.ser.is_open:
            self.ser.close()

            logger.info(f"Access to {self.serial_path} was closed")
        else:
            logger.warning(f"Attempt of repeat disconnect to {self.serial_path}")

        self.disconnect()  # MQTT disconnecting
        exit()

    @logger.catch
    def read_from_serial_loop(self):
        while True:
            data_from_serial: str or None = self.read_from_serial()
            if isinstance(data_from_serial, str):
                self.parse_serial_data(data=data_from_serial)

    @logger.catch
    def _on_mqtt_message(self, client, userdata, msg):
        raw_data: str or Any = msg.payload.decode('utf-8')
        self.parse_mqtt_data(raw_data)

    @logger.catch
    def parse_serial_data(self, data: str) -> None:
        raise NotImplementedError

    @logger.catch
    def parse_mqtt_data(self, data: str) -> None:
        raise NotImplementedError


class RobotSerialToMQTTConnector(BaseSerialToMQTTConnector):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __del__(self):
        RobotSerialToMQTTConnector.__instance = None

    def __init__(self,
                 serial_path: str = os.getenv("SERIAL_PATH"),
                 baudrate: int = int(os.getenv("SERIAL_BAUDRATE")),
                 timeout: int = int(os.getenv("SERIAL_TIMEOUT")),
                 broker: str = os.getenv("EMQX_HOST"), port: int = int(os.getenv("MQTT_PORT")),
                 root_topic: str = os.getenv("COMMAND_TOPIC"), command_topic: str = os.getenv("COMMAND_TOPIC"),
                 mqtt_msg_split_sym: str = os.getenv("MQTT_COMMAND_SPLIT_SYMBOL")):

        BaseSerialToMQTTConnector.__init__(self,
                                           serial_path=serial_path,
                                           baudrate=baudrate, timeout=timeout,
                                           broker=broker, port=port,
                                           root_topic=root_topic, command_topic=command_topic,
                                           mqtt_msg_split_sym=mqtt_msg_split_sym)

        self.sensors_list = [BATTERY(), RFID(), IS(), US()]
        self.devices_list = [CameraServo(), Wheels(), Flashlight(), UVFlashlight()]

        self.msg_to_mqtt: str or None = None

    def parse_serial_data(self, data: str) -> None:
        data = data.strip()
        if data[-1] == "E":
            indicator = data[:2]
            time_now = str(datetime.now())

            for sensor in self.sensors_list:
                if sensor.name == indicator:
                    self.msg_to_mqtt = json.dumps(sensor.set_value(data), indent=4)
                    sensor.last_change_datetime = time_now

                    self.send_message(topic=f"{self.root_topic}{indicator}".replace('//', '/'),
                                      message=self.msg_to_mqtt)
                    break
            else:
                logger.warning(f"A message has been received from serial that is not being processed in any way:{data}")
        else:
            logger.warning(f"An invalid message from serial has arrived: {data}")

    def parse_mqtt_data(self, data: str) -> None:
        """
        :param data: should be in the format`device_name.value(s)`
                     for wheels: WHEELS~+100;-100
        """
        device_from_mqtt: str or None = None
        value_from_mqtt: str or None = None
        try:
            device_from_mqtt, value_from_mqtt = data.split(self.mqtt_msg_split_sym)
        except ValueError:
            logger.error(f"Failed to split the string {data}. Not found this symbol: {self.mqtt_msg_split_sym}")

        if isinstance(device_from_mqtt, str) and isinstance(value_from_mqtt, str):
            device_from_mqtt, value_from_mqtt = device_from_mqtt.upper(), value_from_mqtt.upper()
            for device in self.devices_list:
                if device.name == device_from_mqtt:
                    command_for_serial = device.set_value(value_from_mqtt)

                    self.write_to_serial(command_for_serial)
                    break
            else:
                logger.warning(f"A message has been received from {self.subscribed_topic}"
                               f" that is not being processed in any way: {data}")