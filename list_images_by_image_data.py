import boto3
from boto3.dynamodb.conditions import And, Attr
from functools import reduce

# Constants
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

'''
the parameter 'event' Should look like
{
	"image_data": "{some_image_base64_data}"
}

'''


def lambda_handler(event, context):
    # Read the data from API Request Body
    image_data = event['image_data']
    data_stream = base64.b64decode(image_data)

    # TODO send data_stream to object detection function, for now we mock the result
    object_detection_result = ["people", "dogs"]

    '''
    Query DynamoDB, this command basically means : 
    find records where their tags attributes, contains all the tags from API Request
    so basically dbData.tags.contains(tag1) && dbData.tags.contains(tag2) and so on
    '''
    response = table.scan(FilterExpression=reduce(And, ([Attr("tags").contains(tag) for tag in tags])))

    # Reformat Response Data
    image_url_list = [item['url'] for item in response['Items']]
    return {"links": image_url_list}
