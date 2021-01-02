import os
import numpy as np
from random import shuffle
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.utils import plot_model

from get_data import IMAGE_SHAPE, LABELS
from preprocess_data import preprocess_data



MODEL_CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "model", "checkpoint")


from tensorflow.keras.applications import DenseNet121

def get_model():
    # densenet = DenseNet121(include_top=False, weights='imagenet', classes=3,input_shape=IMAGE_SHAPE)
    # densenet.trainable=True

    # model = keras.Sequential([
    #     densenet,
    #     layers.MaxPool2D(),
    #     layers.Flatten(),
    #     layers.Dense(3, activation='softmax')
    # ])

    model = keras.Sequential([
        layers.Conv2D(16, (3, 3), padding="same", kernel_initializer="random_normal", input_shape=IMAGE_SHAPE),
        layers.Conv2D(16, (3, 3), padding="same", kernel_initializer="random_normal", activation="relu"),
        layers.MaxPool2D((2, 2), padding="same"),

        layers.Conv2D(32, (3, 3), padding="same", kernel_initializer="random_normal"),
        layers.Conv2D(32, (3, 3), padding="same", kernel_initializer="random_normal", activation="relu"),
        layers.MaxPool2D((2, 2), padding="same"),

        layers.Conv2D(64, (3, 3), padding="same", kernel_initializer="random_normal"),
        layers.Conv2D(64, (3, 3), padding="same", kernel_initializer="random_normal", activation="relu"),
        layers.MaxPool2D((2, 2), padding="same"),

        layers.Flatten(),

        layers.Dense(64, kernel_initializer="random_normal", activation="relu"),
        layers.Dense(16, kernel_initializer="random_normal", activation="relu"),
        layers.Dense(4, kernel_initializer="random_normal", activation='softmax')
    ])

    model.compile(loss="categorical_crossentropy", metrics=["acc"])
    return model



def convert_to_cnn_input(data):
    shuffle(data)
    x, y = zip(*data)
    
    # convert to one-hot encoding
    y = [LABELS.index(l) for l in y]
    y = to_categorical(y)

    return x, y


def train_model(model, data):
    x, y = convert_to_cnn_input(data)

    # print(x[0].shape)
    # print(y[0].shape)

    model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
        filepath=MODEL_CHECKPOINT_PATH,
        save_weights_only=True,
        monitor='val_acc',
        mode='max',
        save_best_only=True
    )

    early_stopping_callback = keras.callbacks.EarlyStopping(
        patience=2
    )

    history = model.fit(
        x=np.array(x), y=np.array(y),
        batch_size=4,
        epochs=8,
        validation_split=0.2,
        callbacks=[
            model_checkpoint_callback,
            early_stopping_callback
        ]
    )

    return history


def make_prediction(model, img):
    img = np.array([img])
    res = model.predict(x=img)[0]
    # print(res)
    y_hat = np.argmax(res)  # convert from softmax
    return LABELS[y_hat], res[y_hat]



# ARCHITECTURE_PLOT_PATH = os.path.join(os.path.dirname(__file__), "model_architecture.png")
# print(ARCHITECTURE_PLOT_PATH)


if __name__ == "__main__":
    data = preprocess_data()

    model = get_model()
    model.summary()
    # plot_model(model, to_file=ARCHITECTURE_PLOT_PATH)
    
    history = train_model(model, data)
    print(history)
