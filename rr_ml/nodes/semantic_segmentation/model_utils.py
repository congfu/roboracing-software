import keras
import cv2
import numpy as np


class UNetModelUtils(object):
    def __init__(self):
        self.in_height = 256
        self.in_width = 256

        self.orig_width = None
        self.orig_height = None

        self.n_channels = 5
        self.n_classes = 2

    # significant credit to https://github.com/divamgupta/image-segmentation-keras
    def make_unet_model(self):
        L = keras.layers

        input_layer = L.Input((self.in_height, self.in_width, self.n_channels))

        conv1 = L.Conv2D(32, 3, activation='relu', padding='same')(input_layer)
        conv1 = L.Dropout(0.05)(conv1)
        conv1 = L.Conv2D(32, 3, activation='relu', padding='same')(conv1)

        pool1 = L.AveragePooling2D(pool_size=4)(conv1)  # 32x64

        conv2 = L.Conv2D(32, 3, activation='relu', padding='same')(pool1)

        pool2 = L.AveragePooling2D(pool_size=4)(conv2)  # 16x16

        conv3 = L.Conv2D(1, 3, activation='relu', padding='same')(pool2)
        flat1 = L.Flatten()(conv3)  # 8*16*N flat
        dense2 = L.Dense(self.in_height * self.in_width // 256, activation='relu')(flat1)
        small1 = L.Reshape(target_shape=(self.in_height // 16, self.in_width // 16, 1))(dense2)

        up1 = L.UpSampling2D(size=4)(small1)
        up1 = L.Concatenate(axis=3)([up1, conv2])
        up1 = L.Dropout(0.1)(up1)

        conv4 = L.Conv2D(32, 3, activation='relu', padding='same')(up1)

        up2 = L.UpSampling2D(size=4)(conv4)
        up2 = L.Concatenate(axis=3)([up2, conv1])

        conv6 = L.Conv2D(self.n_classes, 1, padding='same')(up2)
        conv6 = L.Activation('softmax')(conv6)

        model = keras.Model(inputs=input_layer, outputs=conv6)
        return model

    def crop(self, img):
        r = int(img.shape[0] * 0.4)
        self.orig_height, self.orig_width = img.shape[:2]
        return img[r:]

    def uncrop(self, img):
        stack = np.vstack((np.zeros_like(img), img))
        out = stack[-self.orig_height:]
        assert out.shape == (self.orig_height, self.orig_width)
        return out

    def prepare_input(self, raw_img):
        img_resized = cv2.resize(raw_img, (self.in_width, self.in_height))
        img_blurred = cv2.GaussianBlur(img_resized, (7, 7), 0)
        img_hsv = cv2.cvtColor(img_blurred, cv2.COLOR_BGR2HLS)
        img_scaled = img_hsv.astype(np.float32) / np.array([180., 255., 255.])

        img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        # clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8, 8))
        # img_eq = clahe.apply(img_gray)
        img_blurred = cv2.GaussianBlur(img_gray, (15, 15), 0)
        # img_edges = cv2.Canny(img_blurred, 18, 35)
        # img_edges_scaled = img_edges.astype(np.float32) / 255.
        # img_edges_scaled = img_edges_scaled.reshape(img_edges_scaled.shape + (1,))

        sobel1 = cv2.Sobel(img_blurred, cv2.CV_32F, 0, 1, ksize=3)
        sobel2 = cv2.Sobel(img_blurred, cv2.CV_32F, 1, 0, ksize=3)
        sobel_combo = np.stack([sobel1, sobel2], axis=-1)
        sobel_scaled = np.float32(sobel_combo / 255.)

        # cv2.imshow("vis", np.hstack([img_blurred, np.uint8(sobel)]))
        # cv2.waitKey(500)

        return np.concatenate([img_scaled, sobel_scaled], axis=2)
        # return img_scaled

    def load_input(self, fname):
        img = cv2.imread(fname)
        img = self.crop(img)
        return self.prepare_input(img)

    def load_label(self, fname):
        img_label = np.load(fname)
        # label order: 0 background, 1 yellow, 2 white, 3 cones

        onehot_labels = np.zeros(img_label.shape + (self.n_classes,), dtype=np.float32)
        for i, c in [(0, 0), (1, 1), (1, 2)]:
            onehot_labels[:, :, i][img_label == c] = 1.0

        onehot_labels = self.crop(onehot_labels)
        # cv2.imshow("vis", onehot_labels[..., 1])
        # cv2.waitKey(0)
        return cv2.resize(onehot_labels, (self.in_width, self.in_height))

    def prediction_image_bgr8(self, y):
        colors = [(0, 0, 0), (0, 255, 255), (255, 255, 255), (0, 127, 255)]
        my = np.argmax(y, axis=-1)
        img = np.ndarray((self.in_height, self.in_width, 3), dtype=np.uint8)
        for i, color in enumerate(colors):
            mask = (my == i).reshape(img.shape[:2])
            img[mask] = color
        return img

    def prediction_image_mono8(self, y):
        output_img = np.zeros(shape=(self.in_height, self.in_width), dtype=np.uint8)
        argmax_img = np.argmax(y, axis=-1)
        output_img[argmax_img > 0] = 255
        return output_img