import asyncio
import json
import paho.mqtt.client as mqtt
from fastapi import FastAPI
from hashlib import sha256
from recognizer import Recognizer

host = "localhost"
port = 1883
keepalive = 30
send_topic = f"ToLock"
receive_topic = f"FromLock"

app = FastAPI()
app.isAuthorized = True
app.recognizer = Recognizer()
master_tags = ["07081075dcdfa5b91b5c8aac1402f05d28b68563c026f0fe03412c087bf41c9f",
               "9bc6180d675480f93a205652c8477f350aeecd0c21618290c618ba0dfaec9ed5"]
pin = "b2cf84c62d338adb214f88c9e56a42a8e87c17ae5f7eb176bb248b3cb6baa4f7"
client = mqtt.Client(client_id="11111111", clean_session=True)


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic=receive_topic)


def on_message(client, user_data, msg):
    if msg.topic == receive_topic:
        data = json.loads(msg.payload.decode())
        if data.get("action", None) == "pinUnlock":
            pin_input = data.get("pin", None)
            if sha256(pin_input.encode('utf-8')).hexdigest() == pin:
                app.isAuthorized = True
            client.publish(send_topic, json.dumps({"authorized": app.isAuthorized}))
        if data.get("action", None) == "tagUnlock":
            tag_input = data.get("tag", None)
            if sha256(tag_input.encode('utf-8')).hexdigest() in master_tags:
                app.isAuthorized = True
            client.publish(send_topic, json.dumps({"authorized": app.isAuthorized}))
        if data.get("action", None) == "lock":
            app.isAuthorized = False
            client.publish(send_topic, json.dumps({"authorized": app.isAuthorized}))
        if data.get("action", None) == "pir":
            state = data.get("state", None)
            # app.recognizer.recognition_active=state


client.on_message = on_message
client.on_connect = on_connect
client.connect(host, port, keepalive=keepalive)
client.loop_start()


async def check_stream():
    is_valid = await app.recognizer.check_for_verified_person()
    if is_valid:
        app.isAuthorized = True
        app.recognizer.recognition_active = False
        client.publish(send_topic, json.dumps({"authorized": True}),
                       retain=False)


async def add_person_from_stream():
    success = await app.recognizer.add_verified_person()
    if success:
        # TODO: mqtt??
        pass


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/turn_on_recognition")
async def turn_on_recognition():
    if not app.recognizer.recognition_active:
        app.recognizer.recognition_active = True
        asyncio.create_task(check_stream())
    return "Turned on sucessfully!"


@app.post("/turn_off_recognition")
async def turn_off_recognition():
    if app.recognizer.recognition_active:
        app.recognizer.recognition_active = False
    return "Turned off sucessfully!"


@app.post("/add_person")
async def add_person():
    if app.isAuthorized:
        asyncio.create_task(add_person_from_stream())
    return "Turned on adding process!"
