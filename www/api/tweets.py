# -*- coding: utf-8 -*-

from model import User, Tweet, Reply, Friend
from model import Visibility
from model import db
from flask import session
from api import APIError
import json, time, api.friends


def write_tweet(content, photos, visibility=Visibility.All):
    if not content:
        raise APIError('内容不能为空')
    if not isinstance(photos, list):
        photos = []
    if photos.__len__() > 3:
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
    if not Tweet.query.filter_by(id=target_tweet).first():
        raise APIError('指向的说说不存在')

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
    return reply


def get_friends_tweets(offset=0, limit=10, later_than=0):
    current_uid = session['uid']
    
    friends = api.friends.get_friends()
    print later_than
    tweets = [ Tweet.query.filter(Tweet.user==item.to, Tweet.created_at>=later_than).all() for item in friends ]
    res = []
    for i in tweets:
        res.extend(i)
    res.extend(Tweet.query.filter(Tweet.user==current_uid, Tweet.created_at>=later_than).all())
    res.sort(key=lambda tweet: tweet.created_at, reverse=True)

    return res[offset: offset+limit]


def get_users_tweets(uid, offset=0, limit=10, later_than=0):
    current_uid = session['uid']
    uid=int(uid)
    friends = [ friend.to for friend in Friend.query.filter(Friend.user==current_uid, Friend.agree==True).all() ]
    tweets = Tweet.query.filter(Tweet.user==uid, Tweet.created_at>=later_than).order_by(Tweet.created_at.desc()).all()
    print(friends)
    for item in tweets:
        if item.visibility == Visibility.FriendsOnly and not uid in friends and current_uid != uid:
            tweets.remove(item)
    tweets.sort(key=lambda tweet: tweet.created_at, reverse=True)

    return tweets[offset : offset+limit]


def get_replies(tweet_id, offset=0, limit=10, later_than=0):
    current_uid = session['uid']

    this_tweet = Tweet.query.filter_by(id=tweet_id).first()
    replies = Reply.query.filter(Reply.target==tweet_id, Reply.created_at>=later_than).all()
    for item in replies:
        if item.visibility == Visibility.Mutual and ( current_uid != item.user or current_uid != this_tweet.user):
            replies.remove(item)
            continue
    db.session.commit()
    
    return replies[offset: limit+offset]


def remove_tweet(id):
    current_uid = session['uid']

    tweet = Tweet.query.filter_by(id=id).first()
    if not tweet:
        raise APIError('此说说不存在')
    if not tweet.user == current_uid:
        raise APIError('您没有权限删除此说说。必须是自己发的才行。')
    replies = Reply.query.filter_by(target=tweet.id).all()
    for r in replies:
        db.session.delete(r)
    db.session.delete(tweet)
    db.session.commit()

    return {"id": id}


def remove_reply(id):
    current_uid = session['uid']

    reply = Reply.query.filter_by(id=id).first()
    if not reply:
        raise APIError('此回复不存在')
    tweet = Tweet.query.filter_by(id=reply.target).first()
    if not tweet:
        raise APIError('回复对应的说说不存在。')

    if reply.user == current_uid or tweet.user == current_uid:
        db.session.delete(reply)
        db.session.commit()
    else:
        raise APIError('您没有权限删除此条回复')
    return {"id": id}
