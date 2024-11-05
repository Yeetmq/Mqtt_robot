from loguru import logger
from typing import Any
from datetime import datetime
from utils.BaseHardware import Device,Sensor
import os


logs_path = os.getenv("LOGS_PATH")
logs_path += "base_hardware.log".replace('//', '/')
logger.add(sink=logs_path, format="{level} {time} {message}", level="ERROR")


class UVFlashlight(Device):
    def __init__(self):
        super().__init__()

        self.name = "UV_FLASHLIGHT"
        self._message_mask: str = f'SU++{self._mask}00000000E'
        self._value = '000'

    def set_value(self, value: str) -> str or None:
        """
        Set the illumination level from 0 to 100 for the UV flashlight.
        :param value: The level of the uv flashlight.
        :return:      None
        """
        if value.isdigit():
            value = int(value)
            if 0 <= value <= 100:
                uv_flashlight_value: str = str(1000 + value)[1:]
                self._value = uv_flashlight_value

                command_for_serial: str = self._message_mask.replace(self._mask, self._value)
                return command_for_serial
        else:
            logger.error(f"Incorrect value for the uv_flashlight have been entered: {value}")


class Flashlight(Device):
    def __init__(self):
        super().__init__()

        self.name = "FLASHLIGHT"
        self._message_mask: str = f'SU++000{self._mask}00000E'
        self._value = '000'

    def set_value(self, value: str) -> str or None:
        """
        Set the illumination level from 0 to 100 for the flashlight.
        :param value: The level of the flashlight.
        :return:      None
        """

        if value.isdigit():
            value = int(value)
            if 0 <= value <= 100:
                flashlight_value: str = str(1000 + value)[1:]
                self._value = flashlight_value

                command_for_serial: str = self._message_mask.replace(self._mask, self._value)
                return command_for_serial
        else:
            logger.error(f"Incorrect value for the flashlight have been entered: {value}")


class CameraServo(Device):
    def __init__(self):
        super().__init__()

        self.name = "CAMERA_SERVO"
        self._message_mask: str = f'SS{self._mask}0000000000E'

    def set_value(self, angle: str) -> str or None:
        """
        Set the camera servo from the vertical axis to the angle of rotation, which should be from 40 to 140.
        :param angle: The angle of rotation from the vertical axis, from -50 to 50
        :return:      None
        """
        if angle.isdigit():
            angle = int(angle)
            if -50 <= angle <= 50:
                self._value: str = str(1000 + -angle + 90)[1:]

                command_for_serial: str = self._message_mask.replace(self._mask, self._value)
                return command_for_serial
        else:
            logger.error(f"Incorrect value for the flashlight have been entered: {self._value}")


class Wheels(Device):
    def __init__(self):
        super().__init__()

        self.name = "WHEELS"
        self._message_mask: str = f'ST0{"lwdir"}00{"lwval"}{"rwdir"}00{"rwval"}E'
        self._value = {'lw_val': '000', 'rw_val': '000'}

    def set_value(self, value: str) -> str or None:
        """
        Set the power values for the left and right wheels. The values should be in the range from -100 to 100.
        :param value:  Power value for the left wheels and power value for the right wheels.
        :return:      None
        """
        left, right = list(map(int, value.split(";")))

        if (-100 <= left <= 100) and (-100 <= right <= 100):
            lw_val = str(1000 + abs(left))[1:]
            rw_val = str(1000 + abs(right))[1:]
            lw_dir = '+' if left >= 0 else '-'
            rw_dir = '+' if right >= 0 else '-'

            self._value.update({'lw_val': lw_val, 'rw_val': rw_val})

            command_for_serial = self._message_mask. \
                replace("lwdir", lw_dir).replace("lwval", lw_val). \
                replace("rwdir", rw_dir).replace("rwval", rw_val)

            return command_for_serial
        else:
            logger.error(f"Incorrect settings for the wheel have been entered: lw_val: {left}, rw_val: {right}")


class IS(Sensor):
    def __init__(self):
        super().__init__()

        self.name = 'SI'
        self._value = []

    def set_value(self, value: str):
        """
        :param value: A string of the form 'SI{15 digits}E' is expected
        :return:
        """
        self._value = [value[2 + sensor_idx * 3: 5 + sensor_idx * 3] for sensor_idx in range(5)]

        return self._value


class US(Sensor):
    def __init__(self):
        super().__init__()

        self.name = 'SU'
        self._value = []

    def set_value(self, value: str):
        """
        :param value: A string of the form 'SU{15 digits}E' is expected
        :return:
        """
        self._value = [value[2 + sensor_idx * 3: 5 + sensor_idx * 3] for sensor_idx in range(5)]

        return self._value


class BATTERY(Sensor):
    def __init__(self):
        super().__init__()

        self.name = 'SA'
        self._value = ''

    def set_value(self, value: str):
        """
        :param value: A string of the form 'SA{3 digits}E' is expected
        :return:
        """
        self._value = value[2:5]

        return self._value


class RFID(Sensor):
    def __init__(self):
        super().__init__()

        self.name = 'SF'
        self._value = ''

    def set_value(self, value: str):
        return None