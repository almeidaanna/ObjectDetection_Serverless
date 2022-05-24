import boto3
import cv2
import os
import numpy as np
from numpy import argmax
import json
import base64

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)
s3_bucket = "itags-assignment2"

s3_resource = boto3.resource('s3')
dynamodb_resource = boto3.resource('dynamodb')
s3_config_files = "files4a2"

lambda_client = boto3.client('lambda', region_name='us-east-1')


def lambda_handler(event, context):
    if event:
        # s3_bucket = event["Records"][0]['s3']['bucket']['name']
        # image_key = event["Records"][0]['s3']['object']['key']
        # image_url = "https://{}.s3.amazonaws.com/{}".format(s3_bucket,image_key)
        # image_file = s3.get_object(Bucket=s3_bucket, Key=image_key)['Body'].read()
        image_url = event['url']
        image_key = image_url.split('/')[-1]
        image_file = s3.get_object(Bucket=s3_bucket, Key=image_key)['Body'].read()  # REMOVE.

        image_file_string = base64.b64encode(image_file).decode("utf-8")
        print(image_file_string)

        data = {
            "image_data": image_file_string
        }
        lambda_response = lambda_client.invoke(
            FunctionName="obj_detection_no_dynamo",
            InvocationType='RequestResponse',
            Payload=json.dumps(data)
        )
        resp_str = lambda_response['Payload'].read()
        response = json.loads(resp_str)

        print(response)
        object_list = response["body"]

        # object_list = do_prediction(image, net, image_labels)

        print(object_list)
        table.put_item(Item={'imageId': image_key, "tags": object_list, "url": image_url})
