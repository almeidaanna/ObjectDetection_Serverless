import json
import boto3
from boto3.dynamodb.conditions import Attr

# Constants
s3 = boto3.resource('s3')
s3_bucket = 'itags-assignment2'
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

'''
Event Request should be in this format
{
	"url":"https://itag.s3.amazonaws.com/image1.png"
}
'''


def lambda_handler(event, context):
    
    image_url = event['url']

    '''
    Query DynamoDB for data that have that url
    '''
    response = table.scan(FilterExpression=Attr("url").eq(image_url))
    if len(response['Items']) > 0:
        image_id = response['Items'][0]['imageId']
        # Delete data from DynamoDB
        table.delete_item(Key={'imageId': image_id})

        # Delete image from S3
        s3.Object(s3_bucket, image_id).delete()

        return {
            'statusCode': 200,
            'body': json.dumps('Image with url : {} has been deleted from DynamoDB and S3! '.format(image_url))
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps('Image with url : {} Does not exist! '.format(image_url))
        }

