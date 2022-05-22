import json
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client('s3')

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        image_key = unquote_plus(record['s3']['object']['key'])
        image_file = s3.get_object(Bucket=s3_bucket, Key=image_key)

        # TODO Call Object Detection here
        result = ["people", "dogs", "cat"]

        # Save result to DynamoDB
        data = {}
        data['imageId'] = str(image_key)
        data['tags'] = result
        data['url'] = 'https://{}.s3.amazonaws.com/{}'.format(s3_bucket, str(image_key))
        table.put_item(Item=data)
    return {
    'statusCode': 200,
    'body': json.dumps('Records successfully inserted into database...')
    }
