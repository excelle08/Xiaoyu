from model import User, Tweet, Reply, Friend
from model import Visibility
from model import db
from flask import session
from api import APIError
import json, time


def write_tweet(content, photos, visibility=Visibility.All):
    if not content:
        raise APIError('内容不能为空')
    if not isinstance(photos, list):
        photos = []
    if photos.__len__ > 3:
        raise APIError('图片不能超过三张')

    uid = session['uid']

    tweet = Tweet()
    tweet.user = uid
    tweet.content = content
    tweet.photos = json.dumps(photos)
    tweet.visibility = visibility
    tweet.read = False
    tweet.created_at = time.time()

    db.session.add(tweet)
    db.session.commit()
    return tweet


def reply(target_tweet, content, visibility=Visibility.All):
    if not content:
        raise APIError('内容不能为空')

    uid = session['uid']

    reply = Reply()
    reply.user = uid
    reply.content = content
    reply.target = target_tweet
    reply.visibility = visibility
    reply.read = False
    reply.created_at = time.time()

    db.session.add(reply)
    db.session.commit()
