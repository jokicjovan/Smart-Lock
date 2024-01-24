import asyncio
import datetime
import os
from http.client import HTTPException
from io import BytesIO

import cv2
import httpx
import numpy as np
from PIL import Image

from model import VGGFaceModel


def get_face_classifier():
    return cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )


def get_ann_model():
    return VGGFaceModel()


class Recognizer:
    def __init__(self):
        self.light_threshold = 30
        self.recognition_active = False
        self.camera_url = "http://192.168.1.177"
        self.classifier = get_face_classifier()
        self.ann = get_ann_model()
        self.led_intensity = 0

    async def check_for_verified_person(self):
        cap = cv2.VideoCapture(self.camera_url + ":81/stream")
        person = None
        while not person:
            if not self.recognition_active:
                break

            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame. Exiting...")
                break
            if np.mean(frame) < self.light_threshold:
                await self.toggle_led(64)

            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face = self.classifier.detectMultiScale(
                gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )

            for (x, y, w, h) in face:
                face_roi = frame[y:y + h, x:x + w]
                face_roi = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                person = self.ann.check_face(face_roi)
                print(person)

            # for (x, y, w, h) in face:
            #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            # cv2.imshow('Video Stream', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            await asyncio.sleep(0.00001)  # 0.1ms
        cap.release()
        cv2.destroyAllWindows()
        await self.toggle_led(0)
        return person

    async def capture(self):
        await self.toggle_led(192)
        async with httpx.AsyncClient() as client:
            response = await client.get(self.camera_url + "/capture")
            response.raise_for_status()

            # Save the image using OpenCV
            if response.status_code == 200:
                img_stream = BytesIO(response.content)

                # Open the image using PIL
                img = Image.open(img_stream)
                img.save(os.path.join("unauthorized", datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".png"))
        await self.toggle_led(0)

    async def add_verified_person(self):
        cap = cv2.VideoCapture(self.camera_url + ":81/stream")
        new_person_faces = []
        begin_time = datetime.datetime.now()
        await self.toggle_led(64)
        while len(new_person_faces) < 10:
            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame. Exiting...")
                break
            if (datetime.datetime.now() - begin_time).total_seconds() > 120:
                break
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face = self.classifier.detectMultiScale(
                gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )

            for (x, y, w, h) in face:
                face_roi = frame[y:y + h, x:x + w]
                face_roi = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                face = self.ann.check_face(face_roi)
                if face is None:
                    new_person_faces.append(face_roi)

            await asyncio.sleep(0.00001)

        cap.release()
        cv2.destroyAllWindows()
        await self.toggle_led(0)
        if len(new_person_faces) >= 10:
            self.ann.add_face(new_person_faces)
            return True
        return False

    async def toggle_led(self, value):
        if self.led_intensity != value and 0<=value<256:
            self.led_intensity = value
            async with httpx.AsyncClient() as client:
                response = await client.get(self.camera_url + f"/control?var=led_intensity&val={value}")
                response.raise_for_status()
