import numpy as np
import cv2

from train_model import get_model, make_prediction, MODEL_CHECKPOINT_PATH
from preprocess_data import preprocess_data
from image_helpers import crop_image_square, scale_image
from get_data import IMAGE_SHAPE


def load_trained_model():
    model = get_model()
    model.load_weights(MODEL_CHECKPOINT_PATH)
    return model



if __name__ == "__main__":
    model = load_trained_model()

    # data = preprocess_data()
    # img, label = data[0]
    # print(img.shape)

    # pred = make_prediction(model, img)
    # print(pred)

    cam = cv2.VideoCapture(0)

    window_title = "classifier test"
    cv2.namedWindow(window_title)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        
        frame = crop_image_square(frame)
        img = scale_image(frame, IMAGE_SHAPE[:2])
        frame = cv2.flip(frame, 1)

        pred, conf = make_prediction(model, img)
        # print(f"{pred} ({conf * 100:2.0f}%)")

        cv2.putText(
            frame,
            f"{pred} ({conf * 100:2.0f}%)",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            1,
            cv2.LINE_AA
        )
        cv2.imshow(window_title, frame)

        k = cv2.waitKey(1)
        if k&0xff == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break


