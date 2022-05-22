import json
import boto3
import uuid
import base64

s3 = boto3.resource('s3')
s3_bucket_name = 'itags-assignment2'


# Take Image Data and convert it to file and then upload the data to S3
def lambda_handler(event, context):
    # Read the data from API Request Body
    image_data = event['image_data']
    data_stream = base64.b64decode(image_data)

    # Write the data stream into image file
    filename = str(uuid.uuid4()) + ".jpg"
    with open('/tmp/' + filename, 'wb') as f:
        f.write(data_stream)

    # And then upload it to S3 Bucket
    s3.Bucket(s3_bucket_name).upload_file('/tmp/' + filename, filename)

    return {
        'statusCode': 200,
        'body': json.dumps('Image Has been Succesfully Uploaded to S3')
    }
