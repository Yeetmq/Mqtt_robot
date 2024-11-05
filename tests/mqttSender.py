import atexit
import time
from pynput import keyboard
from mqttBase import MQTTBase


if __name__ == "__main__":
    sender = MQTTBase()
    topic = "/python/mqtt/robot/1/command"
    sender.send_message(topic=topic, message="FLASHLIGHT~100")
    time.sleep(5)
    sender.send_message(topic=topic, message="FLASHLIGHT~000")
    sender.send_message(topic=topic, message="UV_FLASHLIGHT~100")
    time.sleep(5)
    sender.send_message(topic=topic, message="UV_FLASHLIGHT~000")
    sender.send_message(topic=topic, message="WHEELS~100;100")
    time.sleep(3)
    sender.send_message(topic=topic, message="WHEELS~100;-100")
    time.sleep(3)
    sender.send_message(topic=topic, message="WHEELS~000;000")
    time.sleep(5)
    sender.send_message(topic=topic, message="CAMERA_SERVO~40")
    time.sleep(3)
    sender.send_message(topic=topic, message="CAMERA_SERVO~-40")

    sender.disconnect()

