import os
import serial
from loguru import logger

logs_path = os.getenv("LOGS_PATH")
logs_path += "base_com.log".replace('//', '/')
logger.add(sink=logs_path, format="{level} {time} {message}", level="INFO")


class COMBase:
    def __init__(self, serial_path: str, baudrate: int, timeout: int):
        if os.path.exists(serial_path):
            self.ser = serial.Serial(port=serial_path, baudrate=baudrate, timeout=timeout)
            self.serial_path = serial_path

            logger.info(f'Connected to {serial_path}')
        else:
            logger.error("Device is not found")
            exit()

    @logger.catch
    def close(self):
        raise NotImplementedError

    def __decode_message(self, msg: bytes, encoding: str = "utf-8") -> str or None:
        try:
            msg = msg.decode(encoding)
            return msg
        except UnicodeDecodeError:
            return None

    def __encode_message(self, msg: str, encoding: str = "utf-8") -> bytes or None:
        try:
            msg = msg.encode(encoding)
            return msg
        except UnicodeEncodeError:
            return None

    def write_to_serial(self, text: str) -> None:
        encoded_message = self.__encode_message(msg=text)

        if isinstance(encoded_message, bytes):
            self.ser.write(encoded_message)
            logger.info(f"The following command is recorded: {text}")
        else:
            logger.warning(f"The following command could not be encoded: {text}")

    def read_from_serial(self, encoding: str = "utf-8") -> str or None:
        data_from_serial: bytes = self.ser.readline()
        decoded_data: str or None = self.__decode_message(data_from_serial, encoding=encoding)

        if isinstance(decoded_data, str):
            logger.info(f"The following message has been received from serial: {decoded_data}")
            return decoded_data
        else:
            logger.warning(f"The following message from serial was not read: {data_from_serial}")
            return None