import cv2
import os

from image_helpers import crop_image_square, rotate_image, scale_image



IMAGE_SHAPE = (300, 300, 3)
assert(IMAGE_SHAPE[0] == IMAGE_SHAPE[1])    # assert square


def capture_images(cam, save_dir, window_title="capture_images", max_count=None):
    cv2.namedWindow(window_title)

    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    img_counter = 0

    while max_count is None or img_counter < max_count:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        
        img = crop_image_square(frame)
        # img = rotate_image(img, -20)

        cv2.imshow(window_title, cv2.flip(img, 1))

        k = cv2.waitKey(1)
        if k&0xff == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k&0xff == 32:
            # SPACE pressed
            img = scale_image(img, IMAGE_SHAPE[:2])
            img_name = f"img_{img_counter}.png"
            img_path = os.path.join(save_dir, img_name)
            cv2.imwrite(img_path, img)
            print(f"{img_name} written to {img_path}")
            img_counter += 1
    
    cv2.destroyAllWindows()



LABELS = [
    "rock",
    "paper",
    "scissors",
    "empty"
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


if __name__ == "__main__":
    cam = cv2.VideoCapture(0)

    for label in LABELS:
        save_dir = os.path.join(DATA_DIR, f"{label}")
        capture_images(cam, save_dir, window_title=label, max_count=15)
    
    cam.release()
