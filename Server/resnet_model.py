from keras_vggface import VGGFace
from keras_vggface import utils
from scipy.spatial.distance import cosine
import os
import numpy as np
import cv2
import pickle


class ResNet50:
    def __init__(self):
        self.embeddings_file_name = 'embeddings.pickle'
        self.authorized_folder_name = 'authorized'
        self.model = VGGFace(model='resnet50',
                             include_top=False,
                             input_shape=(224, 224, 3), pooling='avg')
        self.load_authorized_persons()

    def load_authorized_persons(self):
        (labels, authorized_embeddings) = self.get_authorized_embeddings()
        embedding_dic = {l: em for (l, em) in zip(labels, authorized_embeddings)}
        with open(self.embeddings_file_name, 'wb') as f:
            pickle.dump(embedding_dic, f)

    def add_authorized_person(self, new_person_images):
        authorized_persons_directories = [d for d in os.listdir(self.authorized_folder_name) if
                              os.path.isdir(os.path.join(self.authorized_folder_name, d))]
        if authorized_persons_directories:
            highest_number = max([int(d.split('_')[1]) for d in authorized_persons_directories])
        else:
            highest_number = 0
        new_person_directory = os.path.join(self.authorized_folder_name, f"person_{highest_number + 1}")
        os.makedirs(new_person_directory)

        for i, person_image in enumerate(new_person_images):
            cv2.imwrite(os.path.join(new_person_directory, str(i) + ".png"), person_image)
        self.load_authorized_persons()

    def check_authorization(self, image_unknown):
        with open(self.embeddings_file_name, "rb") as f:
            embedding_dic = pickle.load(f)
        labels = [key for key in embedding_dic.keys()]
        embeddings = [value for value in embedding_dic.values()]
        unknown_embedding = self.get_embedding(image_unknown)
        return self.find_match(labels, embeddings, unknown_embedding)

    def get_embedding(self, image):
        image = cv2.resize(image, (224, 224))
        image = image.reshape(1, 224, 224, 3)
        image = np.array(image, "float32")
        image = utils.preprocess_input(image, version=2)
        embedding = self.model.predict(image)
        return embedding[0]

    def get_embeddings_from_dir(self, dir_path):
        embeddings = []
        for filename in os.listdir(dir_path):
            if filename.endswith("png") or filename.endswith("jpg") or filename.endswith("jpeg"):
                path = os.path.join(dir_path, filename)
                image = cv2.imread(path)
                embedding = self.get_embedding(image)
                embeddings.append(embedding)
        return embeddings

    def get_authorized_embeddings(self):
        authorized_folder_dir = os.path.join(".", self.authorized_folder_name)
        labels = []
        embeddings = []

        for dir_name in os.listdir(authorized_folder_dir):
            path = os.path.join(authorized_folder_dir, dir_name)
            if os.path.isdir(path):
                embeddings.append(self.get_embeddings_from_dir(path))
                labels.append(dir_name)

        return labels, embeddings

    def get_similarity_score(self, known_embeddings, candidate_embedding):
        score = 1
        for embedding in known_embeddings:
            score_temp = cosine(embedding, candidate_embedding)
            score = min(score, score_temp)

        return score

    def find_match(self, labels, known_embeddings, candidate_embedding, match_threshold=0.4):
        scores = []

        for _, embedding_list in enumerate(known_embeddings):
            scores.append(self.get_similarity_score(embedding_list, candidate_embedding))

        min_score = min(scores)
        score_array = np.array(scores)
        if min_score < match_threshold:
            return labels[score_array.argmin()]
        return None
