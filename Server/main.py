import asyncio
import json
import paho.mqtt.client as mqtt

from fastapi import FastAPI
from recognizer import Recognizer

host = "localhost"
port = 1883
keepalive = 30
send_topic = f"ToLock"
receive_topic = f"FromLock"

app = FastAPI()
recognizer = Recognizer()
client = mqtt.Client(client_id="11111111", clean_session=True)


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic=receive_topic)


def on_message(client, user_data, msg):
    if msg.topic == receive_topic:
        data = json.loads(msg.payload.decode())
        print(data)


client.on_message = on_message
client.on_connect = on_connect
client.connect(host, port, keepalive=keepalive)
client.loop_start()


async def check_stream():
    is_valid = await recognizer.check_stream()
    if is_valid:
        client.publish(send_topic, json.dumps({"authorized": True}),
                       retain=False)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/turn_on_recognition")
async def turn_on_recognition():
    if not recognizer.recognition_active:
        recognizer.recognition_active = True
        asyncio.create_task(check_stream())
    return "Turned on sucessfully!"


@app.post("/turn_off_recognition")
async def turn_off_recognition():
    if recognizer.recognition_active:
        recognizer.recognition_active = False
    return "Turned off sucessfully!"
