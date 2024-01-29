import asyncio
import os
import cv2
import httpx
import sklearn.datasets
from PIL import Image
from datetime import datetime
from io import BytesIO

from resnet_model import ResNet50


async def capture(url):
    for i in range(0, 300):
        async with httpx.AsyncClient() as client:
            response = await client.get(url + "/capture")
            img_stream = BytesIO(response.content)
            img = Image.open(img_stream)
            img.save(os.path.join("test", "capture", datetime.now().strftime("%Y%m%d%H%M%S") + ".png"))
            await asyncio.sleep(1)


async def load_images_from_path(imgs_path):
    images = []
    for filename in os.listdir(imgs_path):
        if filename.endswith("png") or filename.endswith("jpg") or filename.endswith("jpeg"):
            path = os.path.join(imgs_path, filename)
            img = cv2.imread(path)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            classifier = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            face = classifier.detectMultiScale(
                img_gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )

            for (x, y, w, h) in face:
                face_roi = img[y:y + h, x:x + w]
                images.append(face_roi)
    return images


async def get_true_pos_false_neg(images_dataset, model):
    false_neg = 0
    for image in images_dataset:
        person = model.check_authorization(image)
        if person is None:
            false_neg += 1
    return len(images_dataset) - false_neg, false_neg


async def get_false_pos(images_dataset, model):
    false_pos = 0
    for image in images_dataset:
        person = model.check_authorization(image)
        if person is not None:
            false_pos += 1
    return false_pos


async def calculate_false_rejection_rate(false_negatives, num_of_imgs):
    return round(false_negatives * 100 / num_of_imgs, 2)


async def calculate_false_acceptance_rate(false_neg, num_of_imgs):
    return round(false_neg * 100 / num_of_imgs, 2)


async def calculate_precision(true_positives, false_positives):
    return round(true_positives / (true_positives + false_positives), 2) * 100


async def calculate_recall(true_positives, false_negatives):
    return round(true_positives / (true_positives + false_negatives), 2) * 100


async def calculate_f1(precision, recall):
    return round(2 * precision * recall / (precision + recall), 2) * 100


async def main():
    # await capture("http://192.168.1.177")

    model = ResNet50()

    images_dataset1 = await load_images_from_path("test/authorized")
    true_positives, false_negatives = await get_true_pos_false_neg(images_dataset1, model)

    data = sklearn.datasets.fetch_lfw_people(color=True)
    images_dataset2 = data["images"][:300]
    # images_dataset2 = await load_images_from_path("test/unauthorized")
    false_positives = await get_false_pos(images_dataset2, model)

    ffr = await calculate_false_rejection_rate(false_negatives, len(images_dataset1))
    far = await calculate_false_acceptance_rate(false_positives, len(images_dataset2))
    precision = await calculate_precision(true_positives, false_positives)
    recall = await calculate_recall(true_positives, false_negatives)
    f1 = await calculate_f1(precision, recall)

    print(f"tested on {len(images_dataset1)} images of authorized person")
    print(f"tested on {len(images_dataset2)} images of unauthorized person")
    print(f"FRR: {ffr} %")
    print(f"FAR: {far} %")
    print(f"Precision: {precision} %")
    print(f"Recall: {recall} %")
    print(f"F1: {f1} %")


asyncio.run(main())
