import cv2
import matplotlib.pyplot as plt
import numpy as np
import sklearn.datasets
import tensorflow.keras.backend as k
from tensorflow.keras import Input
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, GlobalAveragePooling2D, Dense, Lambda
from tensorflow.keras.models import Model, load_model


class SiameseModel:
    def __init__(self):
        self.model = None
        try:
            self.model = load_model("siamese_model")
        except OSError as e:
            data = sklearn.datasets.fetch_olivetti_faces(shuffle=True, random_state=42)
            self.images_dataset = data["images"]
            self.labels_dataset = data["target"]
            self.create_model()
            self.train_model()
            self.model.save("siamese_model")

    def create_model(self):
        feature_extractor = self.create_feature_extractor()
        imgA = Input(shape=(64, 64, 1))
        imgB = Input(shape=(64, 64, 1))
        featA = feature_extractor(imgA)
        featB = feature_extractor(imgB)

        distance = Lambda(self.euclidean_distance)([featA, featB])
        outputs = Dense(1, activation="sigmoid")(distance)
        self.model = Model(inputs=[imgA, imgB], outputs=outputs)
        self.model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])

    def create_feature_extractor(self):
        inputs = Input((64, 64, 1))
        x = Conv2D(96, (11, 11), padding="same", activation="relu")(inputs)
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x = Dropout(0.3)(x)

        x = Conv2D(256, (5, 5), padding="same", activation="relu")(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x = Dropout(0.3)(x)

        x = Conv2D(384, (3, 3), padding="same", activation="relu")(x)
        x = MaxPooling2D(pool_size=(2, 2))(x)
        x = Dropout(0.3)(x)

        pooled_output = GlobalAveragePooling2D()(x)
        pooled_output = Dense(1024)(pooled_output)
        outputs = Dense(128)(pooled_output)

        model = Model(inputs, outputs)
        return model

    def euclidean_distance(self, vectors):
        (featA, featB) = vectors
        sum_squared = k.sum(k.square(featA - featB), axis=1, keepdims=True)
        return k.sqrt(k.maximum(sum_squared, k.epsilon()))

    def calculate_similarity(self, img1, img2):
        img1 = np.expand_dims(img1, axis=-1)
        img1 = np.expand_dims(img1, axis=0)
        img2 = np.expand_dims(img2, axis=-1)
        img2 = np.expand_dims(img2, axis=0)
        return self.model.predict([img1, img2])[0][0]

    def train_model(self):
        images_pair, labels_pair = self.generate_train_image_pairs(self.images_dataset, self.labels_dataset)
        self.model.fit([images_pair[:, 0], images_pair[:, 1]], labels_pair[:], validation_split=0.2, batch_size=64,
                       epochs=100)

    def test_model(self):
        image = self.images_dataset[92]
        test_image_pairs, test_label_pairs = self.generate_test_image_pairs(self.images_dataset, self.labels_dataset,
                                                                            image)

        for index, pair in enumerate(test_image_pairs):
            pair_image1 = np.expand_dims(pair[0], axis=-1)
            pair_image1 = np.expand_dims(pair_image1, axis=0)
            pair_image2 = np.expand_dims(pair[1], axis=-1)
            pair_image2 = np.expand_dims(pair_image2, axis=0)
            prediction = self.model.predict([pair_image1, pair_image2])[0][0]

    def generate_train_image_pairs(self, images_dataset, labels_dataset):
        unique_labels = np.unique(labels_dataset)
        label_wise_indices = dict()
        for label in unique_labels:
            label_wise_indices.setdefault(label,
                                          [index for index, curr_label in enumerate(labels_dataset) if
                                           label == curr_label])

        pair_images = []
        pair_labels = []
        for index, image in enumerate(images_dataset):
            pos_indices = label_wise_indices.get(labels_dataset[index])
            pos_image = images_dataset[np.random.choice(pos_indices)]
            pair_images.append((image, pos_image))
            pair_labels.append(1)

            neg_indices = np.where(labels_dataset != labels_dataset[index])
            neg_image = images_dataset[np.random.choice(neg_indices[0])]
            pair_images.append((image, neg_image))
            pair_labels.append(0)
        return np.array(pair_images), np.array(pair_labels)

    def generate_test_image_pairs(self, images_dataset, labels_dataset, image):
        unique_labels = np.unique(labels_dataset)
        label_wise_indices = dict()
        for label in unique_labels:
            label_wise_indices.setdefault(label,
                                          [index for index, curr_label in enumerate(labels_dataset) if
                                           label == curr_label])

        pair_images = []
        pair_labels = []
        for label, indices_for_label in label_wise_indices.items():
            test_image = images_dataset[np.random.choice(indices_for_label)]
            pair_images.append((image, test_image))
            pair_labels.append(label)
        return np.array(pair_images), np.array(pair_labels)


if __name__ == '__main__':
    img1 = cv2.cvtColor(cv2.imread("data/test/test_1.jpg"), cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(cv2.imread("data/test/test_2.jpg"), cv2.COLOR_BGR2GRAY)

    classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    face1 = classifier.detectMultiScale(
        img1, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    face2 = classifier.detectMultiScale(
        img2, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )

    for (x, y, w, h) in face1:
        temp = img1[y:y + h, x:x + w]
        img1 = cv2.resize(temp, (64, 64), interpolation=cv2.INTER_NEAREST)
        break

    for (x, y, w, h) in face2:
        temp = img2[y:y + h, x:x + w]
        img2 = cv2.resize(temp, (64, 64), interpolation=cv2.INTER_NEAREST)

    # data = sklearn.datasets.fetch_olivetti_faces()
    # img1 = data["images"][0]
    # img2 = data["images"][120]

    plt.imshow(img1)
    plt.show()
    plt.imshow(img2)
    plt.show()

    img1 = np.expand_dims(img1, axis=-1)
    img1 = np.expand_dims(img1, axis=0)
    img2 = np.expand_dims(img2, axis=-1)
    img2 = np.expand_dims(img2, axis=0)
    smm = SiameseModel()
    print(smm.model.predict([img1, img2])[0][0])
