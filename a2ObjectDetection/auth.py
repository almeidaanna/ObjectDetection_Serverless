import base64

import boto3
import json
import requests
import getpass

COGNITO_REGION_NAME = "us-east-1"
CLIENT_ID = "51eb0ahhp1ldueqjr4g1tsvtn7"
TOKEN_TYPE = "Bearer"

cognito_client = boto3.client("cognito-idp", region_name=COGNITO_REGION_NAME)
def register():
    username = input("Enter Email: ").strip()
    first_name = input("Enter Given Name: ").strip()
    last_name = input("Enter Last Name: ").strip()
    print ("Password must have:\n 1. Minimum 8 characters\n 2. A special case character\n 3. A number case character\n 4. A capital character ")
    password = input("Enter Password: ")
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production"

    response = cognito_client.sign_up(ClientId=CLIENT_ID,
                                      Username=username,
                                      Password=password,
                                      UserAttributes=[
                                          {
                                              "Name": "given_name",
                                              "Value": first_name
                                          },
                                          {
                                              "Name": "family_name",
                                              "Value": last_name
                                          },
                                      ])

    access_token = response["AuthenticationResult"]["AccessToken"]
    refresh_token = response["AuthenticationResult"]["RefreshToken"]
    id_token = response["AuthenticationResult"]["IdToken"]

    return [access_token, refresh_token, id_token, True]
  #  verification()

#def verification():


def login():
    # username = input("Enter Email: ").strip()
    # password = getpass.getpass()
    username = "sjai0024@student.monash.edu"
    password = "Qwerty1!"

    # cognito_client = boto3.client("cognito-idp", region_name=COGNITO_REGION_NAME)
    response = cognito_client.initiate_auth(AuthFlow="USER_PASSWORD_AUTH",
                                            ClientId=CLIENT_ID,
                                            AuthParameters={
                                                "USERNAME": username,
                                                "PASSWORD": password
                                            })

    access_token = response["AuthenticationResult"]["AccessToken"]
    refresh_token = response["AuthenticationResult"]["RefreshToken"]
    id_token = response["AuthenticationResult"]["IdToken"]

    # print(access_token)
    # print(refresh_token)
    # print(id_token)
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production"
    return [access_token, refresh_token, id_token, True]


def upload_image(filename, id_token):
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/upload-image"
    with open(filename, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    data = {
        "image_data": image_data
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + id_token
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.json())
    return response

def update_tags(data, id_token):
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/update-tags"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + id_token
    }
    tags = {}
    response = requests.post(url, json=tags, headers=headers)
    print(response.json())
    return response

def list_image_by_tags(tags, id_token):
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/list-images/tags"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + id_token
    }
    response = requests.post(url, json=tags, headers=headers)
    print(response.json())
    return response

def list_image_by_image_data(data, id_token):
    url = " https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/list-images/image-data"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + id_token
    }
    tags = {}
    response = requests.post(url, json=tags, headers=headers)
    print(response.json())
    return response

def delete_image_and_tag(data, id_token):
    url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/delete-image"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + id_token
    }
    tags = {}
    response = requests.post(url, json=tags, headers=headers)
    print(response.json())
    return response

def signout(access_token):
    response = cognito_client.global_sign_out(
        AccessToken=access_token
    )
    return

def main():
    #add if to check if the user exists in the user pool
    [access_token, refresh_token, id_token, logged_in] = login()
    while logged_in:
        print("*********************QUERIES*********************")
        print("[1] Upload Image")
        print("[2] Update Image Tags")
        print("[3] List Image by Tags")
        print("[4] List Image by Image Data")
        print("[5] Delete Image and Tags")
        print("[0] Sign Out")

        choice = input("Please choose from the above menu:")
        if (int(choice)==1):
            filename = input("Enter image filename: ").strip()
            upload_image(filename, id_token)

        elif(int(choice)==2):
            url = input("Please enter an image: ").strip()
            type = input("1 for add or 0 for delete: ").strip()
            tag = input("Enter object names: (comma separated): ").strip()
            tags = tag.split(',')
            data = {
                "url": url,
                "type": type,
                "tags": tags
            }
            update_tags(data, id_token)

        elif(int(choice)==3):
            tag = input("Enter object names: (comma separated): ").strip()
            tags = tag.split(',')
            data = {
                "tags": tags
            }
            list_image_by_tags(data, id_token)

        elif(int(choice)==4):
            filename = input("Enter image filename: ")
            image_data = base64.b64encode(filename.read()).decode('utf-8')
            data = {
                "image data": image_data
            }
            list_image_by_image_data(data, id_token)

        elif(int(choice)==5):
            url = input("Please enter an image: ").strip()
            data = {
                "url": url
            }
            delete_image_and_tag(data, id_token)

        elif (int(choice)==0):
            signout(access_token)
            logged_in = False

        else:
            print("Invalid Option, Please Try Again")

if __name__ == "__main__":
    main()
    # [access_token, refresh_token, id_token] = login()
    # print(upload_image('inputfolder/000000007454.jpg', id_token))
    # tag = input("Enter object names: (comma separated): ") #should make into loop to continuously take tag till user wants to exit
    # tags = tag.split(',')
    # data = {
    #     "tags": tags
    # }
    # print(list_image_by_tags(data, id_token))


