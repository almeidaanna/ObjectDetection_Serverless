# import the necessary packages
import numpy as np
import sys
import time
import cv2
import os
from flask import Flask, request, abort
import base64
import boto3

# construct the argument parse and parse the arguments
confthres = 0.3
nmsthres = 0.1

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1', endpoint_url="http://localhost:8000")
s3 = boto3.resource('s3')
BUCKET_NAME = "test"

s3.Bucket(BUCKET_NAME).upload_file("your/local/file", "dump/file")


def get_labels(labels_path):
    # load the COCO class labels our YOLO model was trained on
    lpath = os.path.sep.join([yolo_path, labels_path])

    print(yolo_path)
    LABELS = open(lpath).read().strip().split("\n")
    return LABELS


def get_weights(weights_path):
    # derive the paths to the YOLO weights and model configuration
    weightsPath = os.path.sep.join([yolo_path, weights_path])
    return weightsPath


def get_config(config_path):
    configPath = os.path.sep.join([yolo_path, config_path])
    return configPath


def load_model(configpath, weightspath):
    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(configpath, weightspath)
    return net


def do_prediction(image, net, LABELS):
    (H, W) = image.shape[:2]
    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416),
                                 swapRB=True, crop=False)
    net.setInput(blob)
    start = time.time()
    layerOutputs = net.forward(ln)
    # print(layerOutputs)
    end = time.time()

    # show timing information on YOLO
    print("[INFO] YOLO took {:.6f} seconds".format(end - start))

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            # print(classID)
            confidence = scores[classID]

            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > confthres:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])

                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres,
                            nmsthres)

    # ensure at least one detection exists
    object_list = []
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            print("detected item:{}, accuracy:{}, X:{}, Y:{}, width:{}, height:{}".format(LABELS[classIDs[i]],
                                                                                          confidences[i],
                                                                                          boxes[i][0],
                                                                                          boxes[i][1],
                                                                                          boxes[i][2],
                                                                                          boxes[i][3]))
            image_object = {"label": LABELS[classIDs[i]], "accuracy": confidences[i],
                            "rectangle": {"height": boxes[i][3], "left": boxes[i][0],
                                          "top": boxes[i][1], "width": boxes[i][2]}}
            object_list.append(image_object)

    return object_list

# method will save images and data tags data into the dynamoDB
def save_to_dynamo_db(data_json, table_name):
    table = dynamodb.Table(table_name)


def upload_to_s3(image_data):
    s3.Bucket(BUCKET_NAME).upload_file("your/local/file", "dump/file")


## argument
if len(sys.argv) != 3:
    raise ValueError("Argument list is wrong. Please use the following format:  {} {} {}".
                     format("python iWebLens_server.py", "<yolo_config_folder>", "<Image file path>"))

yolo_path = str(sys.argv[1])

## Yolov3-tiny versrion
labelsPath = "coco.names"
cfgpath = "yolov3-tiny.cfg"
wpath = "yolov3-tiny.weights"

Lables = get_labels(labelsPath)
CFG = get_config(cfgpath)
Weights = get_weights(wpath)


@app.route("/", methods=['POST'])
def main():
    try:
        if not request.json or 'image' not in request.json or 'id' not in request.json:
            abort(400)
        request_body = eval(request.json)
        id = request_body['id']
        image_base64_encoded = request_body['image']

        # convert the base64_encoded image into file
        image_file = base64.b64decode(image_base64_encoded)
        npimg = np.fromstring(image_file, dtype=np.uint8)
        image = cv2.imdecode(npimg, 1)

        # load the neural net.  Should be local to this method as its multi-threaded endpoint
        nets = load_model(CFG, Weights)
        object_list = do_prediction(image, nets, Lables)
        return {"id": id, "objects": object_list}
    except Exception as e:
        print("Exception  {}".format(e))
        return {"code": "ERROR"}


if __name__ == '__main__':
    # main()
    app.run(port=8010, debug=True, host="0.0.0.0")
