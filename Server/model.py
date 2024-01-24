from keras_vggface import VGGFace
from keras_vggface import utils
from scipy.spatial.distance import cosine
import os
import numpy as np
import cv2
import pickle


class VGGFaceModel:
    def __init__(self):
        self.embedding_file_name = 'embeddings.pickle'
        self.embedding_folder_name = 'processed'
        self.model = VGGFace(model='resnet50',
                             include_top=False,
                             input_shape=(224, 224, 3), pooling='avg')
        self.load_faces()

    def load_faces(self):
        (labels, sys_embeddings) = self.get_sys_embeddings()
        embedding_dic = {l: em for (l, em) in zip(labels, sys_embeddings)}
        with open(self.embedding_file_name, 'wb') as f: pickle.dump(embedding_dic, f)

    def add_face(self, new_person_images):
        person_directories = [d for d in os.listdir(self.embedding_folder_name) if
                              os.path.isdir(os.path.join(self.embedding_folder_name, d))]
        if person_directories:
            highest_number = max([int(d.split('_')[1]) for d in person_directories])
        else:
            highest_number = 0
        new_person_directory = os.path.join(self.embedding_folder_name, f"person_{highest_number + 1}")
        os.makedirs(new_person_directory)

        for i, person_image in enumerate(new_person_images):
            cv2.imwrite(os.path.join(new_person_directory, str(i) + ".png"), person_image)
        self.load_faces()

    def check_face(self, image_unknown):
        with open(self.embedding_file_name, "rb") as f: embedding_dic = pickle.load(f)
        labels = [key for key, value in embedding_dic.items()]
        embeddings = [value for key, value in embedding_dic.items()]
        unknown_embedding = self.get_embedding(image_unknown)
        return self.find_match(embeddings, labels, unknown_embedding)

    def get_embedding(self, image):
        image = cv2.resize(image, (224, 224))
        image = image.reshape(1, 224, 224, 3)
        image = np.array(image, "float32")
        image = utils.preprocess_input(image, version=2)
        embedding = self.model.predict(image)
        return embedding[0]

    def get_embeddings_dir(self, dir_path):
        embeddings = []
        for filename in os.listdir(dir_path):
            if filename.endswith("png") or filename.endswith("jpg") or filename.endswith("jpeg"):
                path = os.path.join(dir_path, filename)
                image = cv2.imread(path)
                embedding = self.get_embedding(image)
                embeddings.append(embedding)
        return embeddings

    def get_sys_embeddings(self):
        embedding_folder_dir = os.path.join(".", self.embedding_folder_name)
        labels = []
        embeddings = []

        for dirName in os.listdir(embedding_folder_dir):
            path = os.path.join(embedding_folder_dir, dirName)
            if os.path.isdir(path):
                embeddings.append(self.get_embeddings_dir(path))
                labels.append(dirName)

        return (labels, embeddings)

    def get_score(self, known_embeddings, candidate_embedding):
        score = 1
        for embedding in known_embeddings:
            score_temp = cosine(embedding, candidate_embedding)
            score = min(score, score_temp)

        return score

    def find_match(self, know_sys_embeddings, labels, candidate_embedding, match_threshold=0.4):
        scores = []

        for _, embedding_list in enumerate(know_sys_embeddings):
            scores.append(self.get_score(embedding_list, candidate_embedding))

        min_score = min(scores)
        score_array = np.array(scores)
        if min_score < match_threshold:
            return labels[score_array.argmin()]

        #print(f"no match found, min score: {min_score} for {labels[score_array.argmin()]}")
        return None