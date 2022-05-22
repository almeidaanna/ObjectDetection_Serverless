from functools import reduce

import boto3
from boto3.dynamodb.conditions import And, Attr

# Constants
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

'''
the parameter 'event' Should look like
{
	"tags": ["person", "desk","cats"]
}

'''


def lambda_handler(event, context):
    tags = set(event['tags'])  # Remove duplicates from request

    '''
    Query DynamoDB, this command basically means : 
    find records where their tags attributes, contains all the tags from API Request
    so basically dbData.tags.contains(tag1) && dbData.tags.contains(tag2) and so on
    '''
    response = table.scan(FilterExpression=reduce(And, ([Attr("tags").contains(tag) for tag in tags])))

    # Reformat Response Data
    image_url_list = [item['url'] for item in response['Items']]
    return {"links": image_url_list}