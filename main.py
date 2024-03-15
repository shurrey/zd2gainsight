import base64
from cachetools import TTLCache
import html
import json
from pprint import pprint
import requests
import sys

import config

gdh_domain = config.config['gdh_domain']
gdh_client_id = config.config['gdh_client_id']
gdh_client_secret = config.config['gdh_client_secret']
zd_domain = config.config['zd_domain']
zd_forum_id = config.config['zd_forum_id']

zd_url = f"{zd_domain}/api/v2/community/topics/{zd_forum_id}/posts"
zd_headers = {
    "Content-Type": "application/json",
}

cache = None

more = True

def set_token():
    endpoint = 'https://' + self.target_url + '/token'

    if cache != None:
        try:
            token = cache['token']

            return
        
        except KeyError:

            pass

    token, expires_in = gdh_auth()
        
    cache = TTLCache(maxsize=1, ttl=expires_in)

    cache['token'] = token


def get_token():
    #if token time is less than a one second then
    # print that we are pausing to clear
    # re-auth and return the new token
    try:
        token = cache['token']

        return token
    except KeyError:
        set_token()

        return cache['token']
        
def gdh_auth():
   
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
   
    body = {
        "grant_type": "client_credentials",
        "client_id": gdh_client_id,
        "client_secret": gdh_client_secret,
        "scope": "write read"
    }

    response = requests.post(f"{gdh_domain}/oauth2/token", data=body, headers=headers)

    auth_json = response.json()

    return auth_json['access_token'], auth_json['expires_in']

def create_post(post):
    url = f"{gdh_domain}/v2/conversations/start?authorId=646&moderatorId=646"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}"
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
        "Authorization": f"Bearer {get_token()}"
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