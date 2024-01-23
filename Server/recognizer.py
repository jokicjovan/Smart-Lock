import asyncio
import cv2
from model import VGGFaceModel


def get_face_classifier():
    return cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )


def get_ann_model():
    return VGGFaceModel()


class Recognizer:
    def __init__(self):
        self.recognition_active = False
        self.stream_url = "http://192.168.1.177:81/stream"
        self.classifier = get_face_classifier()
        self.ann = get_ann_model()

    async def check_for_verified_person(self):
        cap = cv2.VideoCapture(self.stream_url)
        is_valid = False
        while not is_valid:
            if not self.recognition_active:
                break

            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame. Exiting...")
                break

            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face = self.classifier.detectMultiScale(
                gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )

            for (x, y, w, h) in face:
                face_roi = frame[y:y + h, x:x + w]
                face_roi = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
                face = self.ann.check_face(face_roi)
                print(face)
                if face is not None:
                    is_valid = True
                    break

            # for (x, y, w, h) in face:
            #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            # cv2.imshow('Video Stream', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            await asyncio.sleep(0.00001)  # 0.1ms
        cap.release()
        cv2.destroyAllWindows()
        return is_valid

    async def add_verified_person(self):
        cap = cv2.VideoCapture(self.stream_url)
        new_person_faces = []
        while len(new_person_faces) < 10:
            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame. Exiting...")
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

        if len(new_person_faces) >= 10:
            self.ann.add_face(new_person_faces)
            return True
        return False
