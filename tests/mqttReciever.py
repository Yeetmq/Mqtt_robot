# используется для ....

import json
from mqttBase import MQTTBase


def callback(client, userdata, msg) -> None:
    payload = json.loads(msg.payload.decode('utf-8'))
    print(f"Received `{payload}` from `{msg.topic}` topic")

    # TODO данные отправляются очень быстро, даже принятные, с задержкой выводятся


if __name__ == '__main__':
    receiver = MQTTBase()
    receiver.subscribe(topic="/python/mqtt/robot/1/SU", callback_on_message=callback)
    receiver.subscribe(topic="/python/mqtt/robot/1/SI", callback_on_message=callback)
    receiver.subscribe(topic="/python/mqtt/robot/1/SA", callback_on_message=callback)
    receiver.subscribe(topic="/python/mqtt/robot/1/OTHER", callback_on_message=callback)

    receiver.client.loop_forever()  # TODO запихать в метод и работать в отд. потоке, т.к. блокируется отправка данных
