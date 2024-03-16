import base64
from cachetools import TTLCache
import html
import json
from pprint import pprint
import requests
import sys

import auth
import config

gdh_domain = config.config['gdh_domain']
zd_domain = config.config['zd_domain']
zd_forum_id = config.config['zd_forum_id']

zd_url = f"{zd_domain}/api/v2/community/topics/{zd_forum_id}/posts"
zd_headers = {
    "Content-Type": "application/json",
}

more = True

auth = auth.AuthController()


def create_post(post):
    print(f"CREATE POST")
    url = f"{gdh_domain}/v2/conversations/start?authorId=646&moderatorId=646"
    print(f"CREATE POST url {url}")
    token = auth.get_token()
    print(f"CREATE POST get_token {token}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
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
        print(f"CREATE POST: Error {response.status_code} response body: {response.text}")
        return "UNKNOWN"
    
def reply_to_conversation(comment, conversation_id):
    url = f"{gdh_domain}/v2/conversations/{conversation_id}/reply?authorId=646"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth.get_token()}"
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
    print(f"GET POSTS")
    response = requests.request(
        "GET",
        url,
        headers=zd_headers
    )
    #print(f"GET POSTS response {response.text}")
    post_json = response.json()
    #print(f"GET POSTS get_json")
    posts = post_json['posts']
    #print(f"GET POSTS posts {posts}")
    for post in posts:
        #print(f"GET POSTS post {post}")
        conversation_id = create_post(post)

        if conversation_id != "UNKNOWN":
            if post['comment_count'] > 0:
                get_comments(post['id'], conversation_id)
        else:
            print(f"Error processing")#{post}
        
    return(post_json['next_page'])

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


auth_code = auth.set_token()

i=0
url = zd_url

while more:
    try:
        print(f"Calling get_posts {i}")
        new_url = get_posts(url)

        url = new_url
        i+=1
    except Exception as e:
        print (f"no more {e}")
        more = False