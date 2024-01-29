import os

import cv2
import pickle
import numpy as np
import tensorflow as tf
from keras import layers
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from keras.src.utils import image_dataset_from_directory
from keras_vggface import VGGFace
from keras_vggface import utils
from keras.models import load_model
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

tf.get_logger().setLevel('ERROR')


class VGG16:
    def __init__(self):
        self.processed_folder_name = 'processed'
        self.embedding_file_name = 'vgg16.pickle'
        self.model_name = 'vgg16.keras'
        self.class_names = []
        if os.path.exists(self.model_name) and os.path.exists(self.embedding_file_name):
            self.load_model()
        else:
            self.train_model()

    def train_model(self):
        train_data = image_dataset_from_directory(
            self.processed_folder_name,
            validation_split=0.2,
            subset="training",
            seed=123,
            image_size=(224, 224),
            batch_size=32)

        validation_data = image_dataset_from_directory(
            self.processed_folder_name,
            validation_split=0.2,
            subset="validation",
            seed=123,
            image_size=(224, 224),
            batch_size=32)

        self.class_names = train_data.class_names

        normalization_layer = layers.Rescaling(1. / 255)
        train_data = train_data.map(lambda x, y: (normalization_layer(x), y))

        flip_layer = layers.RandomFlip("horizontal_and_vertical")
        rotation_layer = layers.RandomRotation(0.2)
        augment_layers = tf.keras.Sequential([flip_layer, rotation_layer])
        augmented_ds = train_data.map(lambda x, y: (augment_layers(x), y))
        train_data = train_data.concatenate(augmented_ds)

        base_model = VGGFace(model='vgg16',
                             include_top=False,
                             input_shape=(224, 224, 3))
        nb_class = len(self.class_names)
        x = base_model.output
        x = GlobalAveragePooling2D()(x)

        x = Dense(1024, activation='relu')(x)
        x = Dense(1024, activation='relu')(x)
        x = Dense(512, activation='relu')(x)

        out = Dense(nb_class, activation='softmax')(x)

        self.model = Model(inputs=base_model.input, outputs=out)

        for layer in self.model.layers[:len(base_model.layers)]:
            layer.trainable = False

        for layer in self.model.layers[len(base_model.layers):]:
            layer.trainable = True

        train_data = train_data.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
        validation_data = validation_data.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

        self.model.compile(optimizer='Adam',
                           loss=tf.losses.SparseCategoricalCrossentropy(),
                           metrics=['accuracy'])

        self.model.fit(
            train_data,
            batch_size=1,
            validation_data=validation_data,
            verbose=1,
            epochs=10
        )
        self.model.save(self.model_name)

        class_dictionary = {
            index: value for (index, value) in enumerate(self.class_names)
        }
        face_label_filename = self.embedding_file_name
        with open(face_label_filename, 'wb') as f:
            pickle.dump(class_dictionary, f)

    def load_model(self):
        self.model = load_model(self.model_name)

        with open(self.embedding_file_name, "rb") as f: class_dictionary = pickle.load(f)
        self.class_names = [value for _, value in class_dictionary.items()]

    def check_face(self,image_unknown):
        image = cv2.resize(image_unknown, (224, 224))
        image = image.reshape(1, 224, 224, 3)
        image = np.array(image, "float32")
        image = utils.preprocess_input(image, version=2)
        return self.class_names[self.model.predict(image)[0].argmax()]


if __name__ == '__main__':
    model = VGG16()
    imagePath_unknown = 'test/vule.png'
    image_unknown = cv2.imread(imagePath_unknown)

    who=model.check_face(image_unknown)
    print("Predicted face: " +who)
    print("============================\n")
