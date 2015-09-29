from model import db, User, Friend, FriendGroup, BlackList
from flask import session
from api import APIError
import json


def get_friend_groups():
    uid = session['uid']
    group = FriendGroup.query.filter_by(user=uid).first()
    group = json.load(group.content())
    return group


def get_friends():
    uid = session['uid']
    return Friend.query.filter(user==uid, agree==True).all()


def add_friends(target_id, group_id):
    uid = session['uid']
    if not User.query.filter_by(uid=target_id).first():
        raise APIError('目标用户不存在')

    if Friend.query.filter(user=u=id, to==target_id).first():
        raise APIError('此人已经是好友')

    friend = Friend()
    friend.user = uid
    friend.to = target_id
    friend.group = group_id
    friend.agree = False

    db.session.add(friend)
    db.session.commit()
    return friend


def agree_friend(id, group_id):
    uid = session['uid']

    friend = Friend.query.filter_by(id=id).first()
    friend.agree = True

    f2 = Friend()
    f2.user = uid
    f2.to = friend.user
    f2.group = group_id
    f2.agree = True

    db.session.add(f2)
    db.session.commit()
    return f2


def delete_friend(target_id):
    uid = session['uid']
    friend = Friend.query.filter(user==uid, to==target_id).first()
    if not friend:
        raise APIError('指定的好友不存在')

    f2 = Friend.query.filter(user==friend.to, to==friend.user).first()
    f_id = friend
    db.session.delete(friend)
    db.session.delete(f2)
    db.session.commit()
    return {"id": f_id}


def add_to_blacklist(target_id):
    uid = session['uid']
    if not User.query.filter_by(uid=target_id).first():
        raise APIError('指定的用户不存在')

    if BlackList.query.filter(user==uid, to==target_id):
        raise APIError('该用户已经在黑名单')

    blacklist = BlackList()
    blacklist.user = uid
    blacklist.to = target_id
    db.session.add(blacklist)
    db.session.commit()
    return blacklist


def remove_from_blacklist(target_id):
    uid = session['uid']
    blacklist = BlackList.query.filter(user==uid, to==target_id).first():
    if not blacklist:
        raise APIError('指定的用户不在黑名单中')

    b_id = blacklist.id
    db.session.delete(blacklist)
    db.session.commit()
    return {"id": b_id}
