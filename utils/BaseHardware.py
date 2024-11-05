import os
from loguru import logger
from typing import Any
from datetime import datetime

logs_path = os.getenv("LOGS_PATH")
logs_path += "base_hardware.log".replace('//', '/')
logger.add(sink=logs_path, format="{level} {time} {message}", level="ERROR")


class BaseHardware:
    def __init__(self):
        self.name: str or None = None
        self.last_change_datetime: str = str(datetime.now())

        self._mask: str = '@'
        self._value: Any or None = None

    def get_value(self) -> Any:
        return self._value

    def set_value(self, value: Any):
        raise NotImplementedError


class Device(BaseHardware):
    def __init__(self):
        BaseHardware.__init__(self)
        self._message_mask: str or None = None

    def set_value(self, value: int):
        """ In this method, the logic of setting the value should
                                                be implemented by replacing the keywords in the message mask """
        raise NotImplementedError


class Sensor(BaseHardware):
    def __init__(self):
        BaseHardware.__init__(self)

    def set_value(self, value: str):
        """ In this method, the logic of setting the value should be implemented by receiving
                                            a string that should come from the serial port and parsing this string """
        raise NotImplementedError