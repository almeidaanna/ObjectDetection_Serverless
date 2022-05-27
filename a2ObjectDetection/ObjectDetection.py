import re
import string
import boto3

def newfun():
    print(string.punctuation)

def login():
    username = input('Username: ').strip()
    while username.isspace() or (not re.match(username, "@")):
        print("Invalid username, please try again")
        username = input('Username: ').strip().lower()
    password = input('Password: ').strip()
    while password.isspace() or (not re.match(password,string.punctuation)) or (not password.isalnum()):
        print("Invalid password, please try again")
        password = input('Password: ').strip()



def register():
    fname = input('First name: ').strip().lower()
    lname = input('Last Name: ').strip().lower()
    username = input('Username: ').strip()
    password = input('Password: ').strip()
    confirm_password = input('Confirm Password: ').strip()


if __name__ == "__main__":
    login()
