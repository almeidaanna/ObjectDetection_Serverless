import boto3
import cv2
import os
import numpy as np
from numpy import argmax
import json

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)
s3_bucket = "itags-assignment2"

s3_resource = boto3.resource('s3')
dynamodb_resource = boto3.resource('dynamodb')
s3_config_files = "files4a2"

confthres = 0.5
nmsthres = 0.1
def do_prediction(image,net,LABELS):

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
    # start = time.time()
    layerOutputs = net.forward(ln)
    #print(layerOutputs)
    # end = time.time()

    # show timing information on YOLO
    # print("[INFO] YOLO took {:.6f} seconds".format(end - start))

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
            # print(scores)
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

    # TODO Prepare the output as required to the assignment specification
    # ensure at least one detection exists
    list_of_objects = []
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # each_object[i] = {}
            # each_object[i]["label"] = LABELS[classIDs[i]]
            # each_object[i]["accuracy"] = confidences[i]
            # each_object[i]["rectangle"] = {}
            # each_object[i]["rectangle"]["height"] = boxes[i][3]
            # each_object[i]["rectangle"]["left"] = boxes[i][0]
            # each_object[i]["rectangle"]["top"] = boxes[i][1]
            # each_object[i]["rectangle"]["width"] = boxes[i][2]
            list_of_objects.append(LABELS[classIDs[i]].decode())

    return list_of_objects

def lambda_handler(event,context):
    
    if event:
        
        s3_bucket = event["Records"][0]['s3']['bucket']['name']
        image_key = event["Records"][0]['s3']['object']['key']
        image_url = "https://{}.s3.amazonaws.com/{}".format(s3_bucket,image_key)
        image_file = s3.get_object(Bucket=s3_bucket, Key=image_key)['Body'].read()
        # image_url = event['url']
        # image_key = image_url.split('/')[-1]
        # image_file = s3.get_object(Bucket=s3_bucket, Key=image_key)['Body'].read() #REMOVE.
        # print(image_file)
        
        numpy_image_array = np.frombuffer(image_file, np.uint8)
        npimg = cv2.imdecode(numpy_image_array, cv2.IMREAD_COLOR) #Convert the bytes back into an image
        image=npimg.copy()
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image_labels = s3.get_object(Bucket=s3_config_files, Key='coco.names')['Body'].read().strip().splitlines()
        
        s3_resource.Bucket(s3_config_files).download_file('yolov3-tiny.cfg', '/tmp/yolov3-tiny.cfg')
        s3_resource.Bucket(s3_config_files).download_file('yolov3-tiny.weights', '/tmp/yolov3-tiny.weights')
        
        net = cv2.dnn.readNetFromDarknet('/tmp/yolov3-tiny.cfg', '/tmp/yolov3-tiny.weights')
        object_list = do_prediction(image, net, image_labels)
        
        table.put_item(Item={'imageId':image_key,"tags":object_list,"url":image_url})
