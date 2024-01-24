import asyncio
import json
import paho.mqtt.client as mqtt
from fastapi import FastAPI
from hashlib import sha256
from recognizer import Recognizer
import logging

host = "localhost"
port = 1883
keepalive = 30
send_topic = f"ToLock"
receive_topic = f"FromLock"

app = FastAPI()
app.isAuthorized = True
app.recognizer = Recognizer()
app.incorrect_tries=0
master_tags = ["781075dcdfa5b91b5c8aac142f05d28b68563c026f0fe3412c87bf41c9f", "9bc618d675480f93a205652c8477f35aeecdc21618290c618badfaec9ed5"]
app.pin = "b2cf84c62d338adb214f88c9e56a42a8e87c17ae5f7eb176bb248b3cb6baa4f7"
client = mqtt.Client(client_id="11111111", clean_session=True)
loop=asyncio.get_event_loop()
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)


def on_connect(client, userdata, flags, rc):
    client.subscribe(topic=receive_topic)


def on_message(client, user_data, msg):
    if msg.topic == receive_topic:
        data = json.loads(msg.payload.decode())
        if data.get("action", None) == "pinUnlock":
            pin_input = data.get("pin", None)
            if pin_input == app.pin:
                app.isAuthorized = True
                app.recognizer.recognition_active=False
                app.incorrect_tries=0
                logging.info(f"Successful unlock by pin: {pin_input}")
            else:
                app.incorrect_tries+=1
                logging.warning(f"Unsuccessful unlock by pin: {pin_input}")
            if app.incorrect_tries>=3:
                loop.create_task(app.recognizer.capture())
                logging.warning(f"Alarm is on!")
            client.publish(send_topic, json.dumps({"authorized": app.isAuthorized}))
        if data.get("action", None) == "newPin":
            pin_input = data.get("pin", None)
            old_pin=app.pin
            app.pin=pin_input
            logging.info(f"Pin changed from {old_pin} to {pin_input}")
        if data.get("action", None) == "tagUnlock":
            tag_input = data.get("tag", None)
            if tag_input in master_tags:
                app.isAuthorized = True
                app.recognizer.recognition_active=False
                app.incorrect_tries = 0
                logging.info(f"Successful unlock by tag: {tag_input}")
            else:
                app.incorrect_tries += 1
                logging.warning(f"Unsuccessful unlock by tag: {tag_input}")
            if app.incorrect_tries>=3:
                loop.create_task(app.recognizer.capture())
                logging.warning(f"Alarm is on!")

            client.publish(send_topic, json.dumps({"authorized": app.isAuthorized}))
        if data.get("action", None) == "lock":
            app.isAuthorized = False
            client.publish(send_topic, json.dumps({"lock": "locked"}))
            logging.info(f"Locked")
        if data.get("action", None) == "pir":
            state = data.get("state", None)
            app.recognizer.recognition_active=state
            if state:
                loop.create_task(check_stream())
                logging.info(f"Face recognition active")
            else:
                logging.info(f"Face recognition inactive")
        if data.get("action", None) == "capture":
            loop.create_task(add_person_from_stream())


client.on_message = on_message
client.on_connect = on_connect
client.connect(host, port, keepalive=keepalive)
client.loop_start()


async def check_stream():
    person = await app.recognizer.check_for_verified_person()
    if person:
        app.isAuthorized = True
        app.recognizer.recognition_active = False

        logging.info(f"Successfully unlocked {person}'s face")
        client.publish(send_topic, json.dumps({"authorized": True}),
                       retain=False)



async def add_person_from_stream():
    success = await app.recognizer.add_verified_person()
    if success:
        client.publish(send_topic, json.dumps({"capture": "done"}),
                       retain=False)

        logging.info(f"Successfully added new face")
    else:
        client.publish(send_topic, json.dumps({"capture": "fail"}),
                       retain=False)
        logging.info(f"Failed to add new face")



@app.get("/")
async def root():
    return {"message": "Hello World"}

