#from asyncio.windows_events import NULL
import base64
import json
#from urllib import response
from flask import Flask, redirect, render_template, request, url_for
from flask_awscognito import AWSCognitoAuthentication
import requests
import boto3

app = Flask(__name__)
app.config['AWS_DEFAULT_REGION'] = 'us-east-1'
app.config['AWS_COGNITO_DOMAIN'] = 'https://objectdetectionassignment2.auth.us-east-1.amazoncognito.com'
app.config['AWS_COGNITO_USER_POOL_ID'] = 'us-east-1_wvUTu7JmJ'
app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = '51eb0ahhp1ldueqjr4g1tsvtn7'
app.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = ''
app.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:5000/aws_cognito_redirect'

aws_auth = AWSCognitoAuthentication(app)
COGNITO_REGION_NAME = "us-east-1"
COGNITO_DOMAIN = 'https://objectdetectionassignment2.auth.us-east-1.amazoncognito.com'
COGNITO_REDIRECT_URL = "http://localhost:5000"
USER_POOL_ID = "us-east-1_wvUTu7JmJ"
CLIENT_ID = "51eb0ahhp1ldueqjr4g1tsvtn7"
TOKEN_TYPE = "Bearer"
cognito_client = boto3.client("cognito-idp", region_name=COGNITO_REGION_NAME)


@app.route("/")
def home():
    if len(request.args) == 0:
        username=""
        login_message=""
        hide_verification=True
        create_account_message=""
    else:
        username=request.args.get('username')
        login_message=request.args.get('login_message')
        if request.args.get('hide_verification') == "False":
            hide_verification=False
        else:
            hide_verification=True
        create_account_message=request.args.get('create_account_message')
    return render_template('login.html', username=username, hide_verification=hide_verification, login_message=login_message, create_account_message=create_account_message)


@app.route("/homepage", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['email']
        password = request.form['password']
        # username = "sjai0024@student.monash.edu"
        # password = "Qwerty1!"
        try:
            response = cognito_client.initiate_auth(AuthFlow="USER_PASSWORD_AUTH",
                                                    ClientId=CLIENT_ID,
                                                    AuthParameters={
                                                        "USERNAME": username,
                                                        "PASSWORD": password
                                                    })
        except:
            return redirect(url_for('home', create_account_message="", username="", login_message="Invalid Credentials", hide_verification=True))
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            access_token = response["AuthenticationResult"]["AccessToken"]
            refresh_token = response["AuthenticationResult"]["RefreshToken"]
            id_token = response["AuthenticationResult"]["IdToken"]
            return render_template("homepage.html", username=username, id_token=id_token, access_token=access_token, refresh_token=refresh_token)
        else:
            return redirect(url_for('home', login_message="Invalid Credentials", hide_verification=True))
    return redirect(url_for('home', create_account_message="", username="", login_message="", hide_verification="True"))

@app.route('/createAccount', methods=["POST"])
def create_account():
    username = request.form['email']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    try:
        response = cognito_client.sign_up(ClientId=CLIENT_ID,
                                          Username=username,
                                          Password=password,
                                          UserAttributes=[
                                              {
                                                  'Name': 'given_name',
                                                  'Value': first_name
                                              },
                                              {
                                                  'Name': 'family_name',
                                                  'Value': last_name
                                              },
                                          ])
    except Exception as e:
        print(e)
        return redirect(url_for('home', username="", login_message="", hide_verification=True, create_account_message="Account Creation Failed"))
        # return render_template("login.html", hide_verification=True, create_account_message="Account Creation Failed")
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return redirect(url_for('home', username=username, login_message="", hide_verification=False, create_account_message=""))
        #return render_template("login.html", hide_verification=False, username=username)
    return redirect(url_for('home', username="", login_message="", hide_verification=True, create_account_message="Account Creation Failed"))
    # return render_template("login.html", hide_verification=True, create_account_message="Account Creation Failed")


@app.route('/verifyAccount', methods=["GET", "POST"])
def verify_account():
    username = request.form['username']
    verification_code = request.form['verification_code']
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=verification_code
        )
    except:
        return redirect(url_for('home', username=username, login_message="", hide_verification=False, create_account_message="Invalid Verification Code. Try Again"))
        # return render_template("login.html", hide_verification=False, create_account_message="Invalid Verification Code. Try Again", username=username)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return redirect(url_for('home', username="", login_message="", hide_verification=True, create_account_message="\nCreated Account for " + username + "\n Please Sign in."))
        # return render_template("login.html", hide_verification=True, create_account_message="\nCreated Account for " + username + "\n Please Sign in.")
    return redirect(url_for('home', username=username, login_message="", hide_verification=False, create_account_message="Invalid Verification Code. Try Again"))
    # return render_template("login.html", hide_verification=False, create_account_message="Invalid Verification Code. Try Again", username=username)


@app.route('/uploaded', methods=["GET", "POST"])
def uploaded():
    image = request.files['image']
    username = request.form['username']
    id_token = request.form['id_token']
    access_token = request.form['access_token']
    refresh_token = request.form['refresh_token']
    encoded_string = base64.b64encode(image.read()).decode('utf-8')

    api_url = "https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/upload-image"
    data = {
        "image_data": encoded_string
    }
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + id_token}
    response = requests.post(url=api_url, json=data, headers=headers)

    if response.json()['statusCode'] == 200:
        return render_template('homepage.html', upload_message=response.json()['body'], username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
    return render_template('homepage.html', upload_message="Upload Failed", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)


@app.route('/updateImageTag', methods=["GET", "POST"])
def update_image_tag():
    if request.method == "POST":
        url = request.form['url']
        type = int(request.form['type'])
        tagList = request.form['tags'].split(",")
        tags = [s.strip() for s in tagList]
        username = request.form['username']
        id_token = request.form['id_token']
        access_token = request.form['access_token']
        refresh_token = request.form['refresh_token']
        print(tagList)
        print(tags)
        print(type)
        api_url = 'https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/update-tags'
        data = {
            "url": url,
            "type": type,
            "tags": tags
        }
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + id_token}
        response = requests.post(api_url, json=data, headers=headers)
        if response.json()['statusCode'] == 200:
            return render_template('homepage.html', update_image_tag_message=response.json()['body'], username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
        return render_template('homepage.html', update_image_tag_message="Failed to update tags", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)


@app.route('/listByTags', methods=["GET", "POST"])
def list_by_tags():
    if request.method == "POST":
        tagList = request.form['tags'].split(",")
        tags = []
        for tag in tagList:
            tags.append(tag.strip())
        username = request.form['username']
        id_token = request.form['id_token']
        access_token = request.form['access_token']
        refresh_token = request.form['refresh_token']

        api_url = 'https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/list-images/tags'
        data = {
            "tags": tags
        }
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + id_token}
        response = requests.post(api_url, json=data, headers=headers)
        list_by_tags_message = []
        links = response.json()['links']
        if len(links) <= 0:
            list_by_tags_message.append("No Matching Image Found!")
        else:
            for item in links:
                list_by_tags_message.append(item)
        if response.json()['statusCode'] == 200:
            return render_template('homepage.html', list_by_tags_message=list_by_tags_message, username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
        return render_template('homepage.html', list_by_tags_message="Failed to list images", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)


@app.route('/listByImageData', methods=["GET", "POST"])
def list_by_image_data():
    if request.method == "POST":
        image = request.files['image']
        encoded_string = base64.b64encode(image.read()).decode('utf-8')
        username = request.form['username']
        id_token = request.form['id_token']
        access_token = request.form['access_token']
        refresh_token = request.form['refresh_token']

        api_url = 'https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/list-images/image-data'
        data = {
            "image_data": encoded_string
        }
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + id_token}
        response = requests.post(api_url, json=data, headers=headers)
        links = response.json()['links']
        list_by_image_data_message = []
        if len(links) <= 0:
            list_by_image_data_message.append("No Matching Image Found!")
        else:
            for item in links:
                list_by_image_data_message.append(item)
        if response.json()['statusCode'] == 200:
            return render_template('homepage.html', list_by_image_data_message=list_by_image_data_message, username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
        return render_template('homepage.html', list_by_image_data_message="Failed to list images", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)


@app.route('/deleteImage', methods=["GET", "POST"])
def delete_image():
    if request.method == "POST":
        url = request.form['url']
        username = request.form['username']
        id_token = request.form['id_token']
        access_token = request.form['access_token']
        refresh_token = request.form['refresh_token']

        api_url = 'https://lzf1hzzusk.execute-api.us-east-1.amazonaws.com/production/delete-image'
        data = {
            "url": url,
        }
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + id_token}
        response = requests.post(api_url, json=data, headers=headers)
        if response.json()['statusCode'] == 200:
            return render_template('homepage.html', delete_image_nessage=response.json()['body'], username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
        return render_template('homepage.html', delete_image_nessage="Image Deletion Failed", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)


@app.route('/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        username = request.form['username']
        id_token = request.form['id_token']
        access_token = request.form['access_token']
        refresh_token = request.form['refresh_token']
        try:
            response = requests.get(url=COGNITO_DOMAIN+"/logout?"+"client_id="+CLIENT_ID+"&logout_uri="+COGNITO_REDIRECT_URL)
        except Exception as e:
            print(e)
            return render_template('homepage.html', logout_message="Logout Failed", username=username, access_token=access_token, refresh_token=refresh_token, id_token=id_token)
        return redirect(response.url)

if __name__ == "__main__":
    app.run()
