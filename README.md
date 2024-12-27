# Ghost-Listmonk Bridge
A flask app that serves as a bridge between Ghost and Listmonk

Ghost is a neat open-source blogging platform that allows for easy self-hosting. However, currently its mailing list feature relies on using a corporate service.

Listmonk is an open-source mailing list application that allows for easy self-hosting.

Wouldn't it be nice to use them together, so that Listmonk provides the mailing list functionality for your Ghost blog?

This flask app shows that it can be done using the Ghost webhook feature together with the Listmonk API. The flask app serves as a bridge.

I wrote this to solve a very local problem, with Ghost and Listmonk running on the same machine. But the webhook requests are authenticated, so it should be all right to run this across a network. The code doesn't cover all of Ghost's webhook options, only the following:

1. When a Ghost subscriber is added, a subscriber with the same details gets added to Listmonk's subscriber list
2. When a Ghost subscriber is removed, a subscriber with the same details gets removed from Listmonk's subsriber list
3. When a new Ghost post is published, a new Listmonk campaign with the same details is created and scheduled for publication

Ghost offers some more webhook options, and it should be easy to expand the bridge if I (or you) ever need them.

## Ghost Settings panel
1. Add a custom integration
2. Then, add required webhooks to the integration
3. Supply flask server address, e.g. http://127.0.0.1:5000/webhook (if Ghost runs in the same local setup)
4. Make up a secret to use for authentication
5. Flask app: Fill out `secret` variable in `app.py`

## Listmonk admin panel
1. Create new API user
2. Flask app: Fill out user name and access token in `app.py`
3. Create a list for your Ghost blog
4. Flask app: Fill out the list number (top left corner) in `app.py`

Run flask app and the bridge should be live. 
  
