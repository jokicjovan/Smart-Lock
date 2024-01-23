from keras_vggface import VGGFace
from keras_vggface import utils
import os
import numpy as np
from scipy.spatial.distance import cosine
import cv2
import pickle

batch_size = 32
img_height = 224
img_width = 224

model = VGGFace(model='resnet50',
                include_top=False,
                input_shape=(224, 224, 3), pooling='avg')

def get_embedding(image):
    image = cv2.resize(image, (224, 224))
    image = image.reshape(1, 224, 224, 3)
    image = np.array(image, "float32")
    image = utils.preprocess_input(image, version=2)
    embedding = model.predict(image)
    return embedding[0]


def get_emmbeddings_dir(dir_path):
    embeddings = []
    # enumerate files
    for filename in os.listdir(dir_path):
        if filename.endswith("png") or filename.endswith("jpg") or filename.endswith("jpeg"):
            path = os.path.join(dir_path, filename)
            image = cv2.imread(path)
            embedding = get_embedding(image)
            embeddings.append(embedding)
    return embeddings


def get_sys_embeddings():
    embedding_folder_name = 'processed'
    embedding_folder_dir = os.path.join(".", embedding_folder_name)

    labels = []
    embeddings = []

    for dirName in os.listdir(embedding_folder_dir):
        path = os.path.join(embedding_folder_dir, dirName)
        if os.path.isdir(path):
            embeddings.append(get_emmbeddings_dir(path))
            labels.append(dirName)

    return (labels, embeddings)

(labels, sys_embeddings) = get_sys_embeddings()

embedding_dic = {
    l: em for (l, em) in zip(labels, sys_embeddings)
}
embedding_file_name = 'embeddings.pickle'
with open(embedding_file_name, 'wb') as f: pickle.dump(embedding_dic, f)


def get_score(known_embeddings, candidate_embedding):
    score = 1
    for embedding in known_embeddings:
        score_temp = cosine(embedding, candidate_embedding)
        score = min(score, score_temp)

    return score


def find_match(know_sys_embeddings, labels, candidate_embedding, match_thres=0.4):
    scores = []

    for _, embedding_list in enumerate(know_sys_embeddings):
        scores.append(get_score(embedding_list, candidate_embedding))

    min_score = min(scores)
    score_array = np.array(scores)
    if min_score < match_thres:
        return labels[score_array.argmin()]

    print(f"no match found, min score: {min_score} for {labels[score_array.argmin()]}")
    return None

embedding_file_name = "embeddings.pickle"
with open(embedding_file_name, "rb") as f: embedding_dic = pickle.load(f)

labels = [key for key, value in embedding_dic.items()]
embeddings = [value for key, value in embedding_dic.items()]

imagePath_unknown = 'test/person_1.jpg'
# TODO: Detect only face
image_unknown = cv2.imread(imagePath_unknown)
unknown_embedding = get_embedding(image_unknown)

print(find_match(embeddings, labels, unknown_embedding ))