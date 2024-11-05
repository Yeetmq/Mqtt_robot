FROM python:3.9.18-slim-bullseye

WORKDIR /com_to_mqtt

COPY . /com_to_mqtt
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["bash"]
