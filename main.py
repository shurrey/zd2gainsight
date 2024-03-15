import requests
from pprint import pprint
import base64
import sys
import html
import json

gdh_domain="https://api2-us-west-2.insided.com"
client_id = "09df829c-8010-4ae7-a27c-56a52c86d871"
client_secret = "4db1a1319c60a8b6ca1f3f6fd040f4e6369acde1f3c8e9ba289b1fd14beb1bf1"



DEV_FORUM_ID = "360001932973"
zd_url = f"https://support.box.com/api/v2/community/topics/{DEV_FORUM_ID}/posts"
zd_headers = {
    "Content-Type": "application/json",
}

auth_code = ""

more = True

def gdh_auth():
   
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
   
    body = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "write read"
    }

    response = requests.post(f"{gdh_domain}/oauth2/token", data=body, headers=headers)

    auth_json = response.json()

    return auth_json['access_token']

def create_post(post):
    url = f"{gdh_domain}/v2/conversations/start?authorId=646&moderatorId=646"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_code}"
    }

    payload = {
        "title": post['title'],
        "content": post['details'],
        "categoryId": 24,   
        "tags": [
            "developer",
            "archive"
        ]
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.ok:
        location = response.headers['Location']
        conversation_id = location.split('/')[3]

        return conversation_id
    else:
        print(f"Error {response.status_code} response body: {response.text}")
        return None
    
def reply_to_conversation(comment, conversation_id):
    url = f"{gdh_domain}/v2/conversations/{conversation_id}/reply?authorId=646"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_code}"
    }

    payload = {
        "content": comment['body']
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)

    if response.ok:
        print(f"response body: {response.text}")
    else:
        print(f"Error {response.status_code} response body: {response.text}")
        return None

def get_posts(url):

    response = requests.request(
        "GET",
        url,
        headers=zd_headers
    )

    post_json = response.json()
    
    posts = post_json['posts']
    
    for post in posts:
        
        try:
            conversation_id = create_post(post)

            if post['comment_count'] > 0:
                get_comments(post['id'], conversation_id)
        except:
            print("Error processing {post}")
        
    print(f"return next page")
    return(post_json['next_page'])

def get_first_post_test():

    response = requests.request(
        "GET",
        zd_url,
        headers=zd_headers
    )

    post_json = response.json()
    
    posts = post_json['posts']
    
    for post in posts:
        conversation_id = create_post(post)
        print(f"conversation_id {conversation_id}")
        return

def get_comments(post_id, conversation_id):
    url = f"https://support.box.com/api/v2/community/posts/{post_id}/comments"

    response = requests.request(
        "GET",
        url,
        headers=zd_headers
    )

    comments_json = response.json()
    
    comments = comments_json['comments']
    
    for comment in comments:
        reply_to_conversation(comment, conversation_id)

auth_code = gdh_auth()

i=0
url = zd_url

while more:
    try:
        print(f"Calling get_posts {i}")
        new_url = get_posts(url)

        url = new_url
        i+=1
    except:
        print (f"no more")
        more = False