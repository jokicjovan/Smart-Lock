import asyncio
import os
import cv2

from siamese_model import SiameseModel


class Recognizer:
    def __init__(self):
        self.allowed_faces = []
        allowed_faces_path = "data/allowed"
        for filename in os.listdir(allowed_faces_path):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                file_path = os.path.join(allowed_faces_path, filename)
                self.allowed_faces.append(cv2.resize(cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2GRAY),
                                                     (64, 64), interpolation=cv2.INTER_NEAREST))

        self.recognition_active = False
        self.stream_url = "http://192.168.1.177:81/stream"
        self.classifier = self.get_face_classifier()
        self.ann = self.get_snn()

    async def check_stream(self):
        cap = cv2.VideoCapture(self.stream_url)
        is_valid = False
        while True:
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
                face_roi = cv2.resize(face_roi, (64, 64), interpolation=cv2.INTER_NEAREST)
                is_valid = self.check_face(face_roi)
                if is_valid:
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

    def check_face(self, face_roi):
        for face in self.allowed_faces:
            similarity = self.ann.calculate_similarity(face, face_roi)
            if similarity > 0.7:
                return True
        return False

    def get_face_classifier(self):
        return cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def get_snn(self):
        return SiameseModel()
