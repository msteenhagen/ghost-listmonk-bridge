#! /usr/bin/python3

from flask import Flask, request, Response
import json
import requests
from datetime import date, datetime, time, timedelta
import hashlib
import hmac

# Ghost webhook secret 
secret = 'abcdefghijAbCdEfGhIjAbABCDEFGHIJ'

# Listmonk api details:
base_url = "https://example.com" # Listmonk application url, used for API requests
access_token = 'token api_user_name:ABCDEFGHIJabcdefghijAbCdEfGhIjAb' # Listmonk access token, create Listmonk API user for this with <api_user_name>, and associated token
list_no = 1 # Listmonk list information (to which list should users and campaigns be added)

# Prepares a header for API requests
request_headers = {"Authorization": access_token} 

# API post creates a new Listmonk subscriber
def new_subscriber(request, request_headers):
    email = request['member']['current']['email']
    name = request['member']['current']['name']
    new_subscriber = {
        "email": email,
        "name": name,
        "status": "enabled",
        "lists": [
                list_no
            ],
        "preconfirm_subscriptions": False
        }
    response = requests.post(url= base_url + "/api/subscribers", headers = request_headers, json=new_subscriber)

# API post creates a new Listmonk campaign
def new_post(request, request_headers):
    post_title = request['post']['current']['title']
    post_content = request['post']['current']['html']
    post_plain = request['post']['current']['plaintext']
    heading_line = "<h1>{title}</h1>".format(title = post_title)
    url_line = '<hr><p> Read this article on <a href="{url}">My Ghost Blog</a>'.format(url = request['post']['current']['url'])
    post_content = heading_line + post_content + url_line
    campaign = {
        "name":"A new post",
        "subject":post_title,
        "lists":[list_no],
        "from_email":"Sender Name <noreply@example.com>",
        "content_type":"html",
        "body": post_content,
        "altbody": post_plain,
        "messenger":"email",
        "type":"regular",
        "tags":["test"],
        "template_id":1,
        "send_at": str((datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        }
    response = requests.post(url= base_url + "/api/campaigns", headers = request_headers, json=campaign)
    return response.json()['data']['id']

# API put schedules a Listmonk campaign
def schedule_campaign(request_headers, id):
    campaign = { 
        "status": "scheduled"
    }
    response = requests.put(url= base_url + "/api/campaigns/" + str(id) + "/status", headers = request_headers, json=campaign)    

# API delete deletes a Listmonk subscriber
def delete_subscriber(request, request_headers, id):
    if id > 0:
        response = requests.delete(url= base_url + "/api/subscribers/" + str(id), headers = request_headers)

# API get returns id of Listmonk subscriber
def find_listmonk_subscriber(request_headers, email):
    id = 0
    response = requests.get(url= base_url + "/api/subscribers", headers = request_headers)
    for subscriber in response.json()['data']['results']:
        if subscriber['email'] == email:
            id = subscriber['id']        
    return id   

# Receive webhook request data and decide what to do with it (new post, new subscriber, delete subscriber)
def receive(request):
    if next(iter(request)) == 'post':
        id = new_post(request, request_headers)
        schedule_campaign(request_headers, id)
    elif next(iter(request)) == 'member':
        if request['member']['current']:
            new_subscriber(request, request_headers)
        else:
            email = request['member']['previous']['email']
            id = find_listmonk_subscriber(request_headers, email)
            delete_subscriber(request, request_headers, id)

# Authenticates Ghost webhook using shared secret and receives request when valid
def authenticate(request, secret):
    if "X_GHOST_SIGNATURE" in request.headers:
        [sha_hmac, timestamp] = request.headers.get("X_GHOST_SIGNATURE").split(',')
        received_hmac = sha_hmac.split('=')[1]
        recPayLoad = request.data + timestamp.split('=')[1].encode()
        gen_hmac = hmac.new(secret.encode(), recPayLoad, hashlib.sha256).hexdigest()
        if gen_hmac == received_hmac:
            receive(request)
            return 200
        else:
            return 400
    else:
        return 400

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def respond():
    code = authenticate(request, secret);
    return Response(status=code)
if __name__ == '__main__':
    app.run()
