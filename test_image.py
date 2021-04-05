# import the necessary packages
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import argparse
import imutils
from imutils import paths
import cv2
import random
from pprint import pprint
import sys
import os

from debug_print import debug_print
print = debug_print()

from PIL import ImageFont, ImageDraw, Image

class CvPutJaText:
    def __init__(self):
        pass

    @classmethod
    def puttext(cls, cv_image, text, point, font_path, font_size, color=(0,0,0)):
        font = ImageFont.truetype(font_path, font_size)

        cv_rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cv_rgb_image)

        draw = ImageDraw.Draw(pil_image)
        draw.text(point, text, fill=color, font=font)

        cv_rgb_result_image = np.asarray(pil_image)
        cv_bgr_result_image = cv2.cvtColor(cv_rgb_result_image, cv2.COLOR_RGB2BGR)

        return cv_bgr_result_image

def pil2cv(imgPIL):
    imgCV_RGB = np.array(imgPIL, dtype = np.uint8)
    imgCV_BGR = np.array(imgPIL)[:, :, ::-1]
    return imgCV_BGR

def cv2pil(imgCV):
    imgCV_RGB = imgCV[:, :, ::-1]
    imgPIL = Image.fromarray(imgCV_RGB)
    return imgPIL

def cv2_putText_2(img, text, org, fontFace, fontScale, color):
    x, y = org
    b, g, r = color
    colorRGB = (r, g, b)
    imgPIL = cv2pil(img)
    draw = ImageDraw.Draw(imgPIL)
    fontPIL = ImageFont.truetype(font = fontFace, size = fontScale)
    w, h = draw.textsize(text, font = fontPIL)
    draw.text(xy = (x,y-h), text = text, fill = colorRGB, font = fontPIL)
    imgCV = pil2cv(imgPIL)
    return imgCV



os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = ""

class NotFoundError(Exception):
    pass

def get_unused_dir_num(pdir, pref=None):
    os.makedirs(pdir, exist_ok=True)
    dir_list = os.listdir(pdir)
    for i in range(1000):
        search_dir_name = "" if pref is None else (
            pref + "_" ) + '%03d' % i
        if search_dir_name not in dir_list:
            return os.path.join(pdir, search_dir_name)
    raise NotFoundError('Error')


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", default=None,
	help="path to trained model model")
ap.add_argument("-i", "--image",
	help="path to input image")

args = vars(ap.parse_args())
if(args["image"] is None and args["directory"] is None):
	ap.error("missing arguments -d / --directory and -i / --images")

class_path = os.path.join(os.path.dirname(args["model"]), "classes.txt")
model_path = args["model"] if args["model"] != None else class_path.split(".")[0]+".h5"
image_path = args["image"]
output_dir = get_unused_dir_num(pdir="results", pref=None)

os.makedirs(output_dir, exist_ok=True)

# load the image

image = cv2.imread(image_path)

orig = image.copy()

# load the trained convolutional neural network
print("[INFO] loading network...")
model = load_model(model_path)

img_width = model.layers[0].input.shape[2]
img_height = model.layers[0].input.shape[1]
try:
    model_image_size = (int(img_width), int(img_height))
    image = cv2.resize(image, model_image_size)
except:
    pass


# pre-process the image for classification
image = image.astype("float") / 255.0
image = img_to_array(image)
image = np.expand_dims(image, axis=0)

# classify the input image
predict = model.predict(image)
print(predict)

class_names = open(class_path, 'r')
class_names = [line.split('\n')[0] for line in class_names.readlines()]
pprint(class_names)

# build labels
labels = []
labels.append("{}".format(class_names))
labels.append(" : ".join(["{:.2f}%".format(100*score) for score in predict[0]]))

# draw the label on the image
output_image = imutils.resize(orig, width=400)
fontPIL = "Dflgs9.ttc"
font_path = fontPIL
for i, label in enumerate(labels):
	# cv2.putText(output_image, label, (10, 25 * (i+1)),  cv2.FONT_HERSHEY_SIMPLEX,
	# 	0.7, (0, 255, 0), 2)
	# cv2_putText_2(output_image, label, (10, 25 * (i+1)),  fontPIL,
	# 	10, (0, 255, 0))
    output_image = CvPutJaText.puttext(output_image, label, (10, 25 * (i+1)), font_path, 20, (0, 255, 0))
    # cv2.namedWindow("result", cv2.WINDOW_NORMAL)
    # cv2.imshow("result", output_image)

    # key = cv2.waitKey(60000)#pauses for 3 seconds before fetching next image
    # if key == 27:#if ESC is pressed, exit loop
    #     cv2.destroyAllWindows()
    #     break
# def cv2_putText_2(img, text, org, fontFace, fontScale, color):

    output_path = os.path.join(output_dir, os.path.basename(image_path))
    print(output_path)
    cv2.imwrite(output_path, output_image)