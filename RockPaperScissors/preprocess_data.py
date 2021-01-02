import os
import cv2
import numpy as np
from random import randint, uniform
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from get_data import DATA_DIR, LABELS
from image_helpers import scale_image, rotate_image, zoom_image



# def preprocess_data():
#     ImageDataGenerator(
#         rotation_range=30,
#         zoom_range=0.25,
#         width_shift_range=0.10,
#         height_shift_range=0.10,
#         shear_range=0.10,
#         horizontal_flip=True,
#         fill_mode="nearest"
#     )



def preprocess_data():
    data = []
    for label in LABELS:
        data_subdir = os.path.join(DATA_DIR, label)
        for filename in os.listdir(data_subdir):
            img = cv2.imread(os.path.join(data_subdir, filename))
            data.append((img, label))
            # data.append((cv2.flip(img, 1), label))  # horizontally flipped
    
    augmented_data = []
    for (img, label) in data:
        for _ in range(5):
            augmented_data.append(
                (rotate_image(img, randint(-15, 15)), label)
            )

            augmented_data.append(
                (zoom_image(img, uniform(0.8, 1.0)), label)
            )
    
    return augmented_data


if __name__ == "__main__":
    augmented_data = preprocess_data()
    print(len(augmented_data))
    
    for (img, label) in augmented_data:
        cv2.imshow(label, img)
        k = cv2.waitKey()
        if k&0xff == 27:
            # ESC pressed
            break
    cv2.destroyAllWindows()