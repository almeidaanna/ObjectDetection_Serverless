import boto3
from boto3.dynamodb.conditions import And, Attr
from functools import reduce
import base64
import cv2
import os
import numpy as np
from numpy import argmax
import json

# Constants
s3_bucket = "itags-assignment2"
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

s3_resource = boto3.resource('s3')
dynamodb_resource = boto3.resource('dynamodb')
s3_config_files = "files4a2"
lambda_client = boto3.client('lambda', region_name='us-east-1')

confthres = 0.5
nmsthres = 0.1

'''
the parameter 'event' Should look like
{
	"image_data": "{some_image_base64_data}"
}

'''


def lambda_handler(event, context):
    # Read the data from API Request Body
    image_data = event['image_data']

    # TODO send data_stream to object detection function, for now we mock the result
    data = {
        "image_data": image_data
    }
    lambda_response = lambda_client.invoke(
        FunctionName="obj_detection_no_dynamo",
        InvocationType='RequestResponse',
        Payload=json.dumps(data)
    )

    resp_str = lambda_response['Payload'].read()
    response = json.loads(resp_str)

    print(response)
    object_detection_result = response["body"]
    # object_detection_result = ["chair"]

    '''
    Query DynamoDB, this command basically means : 
    find records where their tags attributes, contains all the tags from API Request
    so basically dbData.tags.contains(tag1) && dbData.tags.contains(tag2) and so on
    '''
    response = table.scan(
        FilterExpression=reduce(And, ([Attr("tags").contains(tag) for tag in object_detection_result])))

    # Reformat Response Data
    image_url_list = [item['url'] for item in response['Items']]
    return {"links": image_url_list}
