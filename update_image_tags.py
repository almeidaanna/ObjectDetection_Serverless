import json

import boto3
from boto3.dynamodb.conditions import Attr

# Constants
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'object_detection_tags'
table = dynamodb.Table(TABLE_NAME)

'''
Event Request should be in this format
{
	"url":"https://itag.s3.amazonaws.com/image1.png", 
	"type": 1,
	"tags": ["person","alex" ]
}
'''


def lambda_handler(event, context):
    image_url = event['url']

    '''
    Query DynamoDB for data that have that url
    '''
    response = table.scan(FilterExpression=Attr("url").eq(image_url))
    print(response)
    if len(response['Items']) > 0:
        to_be_updated_item = response['Items'][0]
        update_type = event['type']

        current_tags = to_be_updated_item['tags']
        print(current_tags)
        # update
        request_tags = event['tags']
        if update_type == 1:
            # combine the current tags & new tags, also remove duplicates with set()
            current_tags.extend(request_tags)
            to_be_updated_item['tags'] = set(current_tags)
        else:
            # remove the request tags from current tags
            to_be_updated_item['tags'] = set(current_tags) - set(request_tags)

        print("Image : {}, Newly Update tags : {}", image_url, to_be_updated_item['tags'])
        table.put_item(Item=to_be_updated_item)

    return {
        'statusCode': 200,
        'body': json.dumps('Tags has been sucessfully updated!!')
    }
