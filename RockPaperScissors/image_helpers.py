import cv2
import numpy as np


def crop_image_square(img):
    w, h, _ = img.shape
    s = min(w, h)
    cropped_img = img[
        (w - s)//2 : -(w - s + 1)//2,
        (h - s)//2 : -(h - s + 1)//2
    ]
    return cropped_img


def scale_image(img, dsize):
    scaled_img = cv2.resize(img, dsize=dsize)
    return scaled_img


def zoom_image(img, factor):
    s = img.shape[0]
    margin = int((1 - factor) * s // 2)
    if margin == 0: return img
    # print(margin)
    cropped_img = img[
        margin:-margin,
        margin:-margin
    ]
    scaled_img = scale_image(cropped_img, (s, s))
    return scaled_img


def rotate_image(image, angle, crop=True):
    assert(abs(angle) <= 15)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

    if crop:
        s = image.shape[0]
        margin = s * 0.09   # maximum possible margin (i.e. 15 degrees)
        margin=int(margin)
        result = result[
            margin:-margin,
            margin:-margin,
        ]
        result = scale_image(result, (s, s))

    return result