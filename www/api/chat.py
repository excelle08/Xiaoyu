# -*- coding: utf-8 -*-

from model import db
from model import ChatMessage, Friend, BlackList
from flask import session
from api import APIError
import api.friends
import time, json
from sqlalchemy import or_, and_

def send(msg_from, to, content):
    f = Friend.query.filter(Friend.user==msg_from, Friend.to==to).first()
    if not f:
        raise APIError('非好友关系不能发送信息~')
    bk = BlackList.query.filter()

    if api.friends.am_i_blocked(to):
        raise APIError('您被拉黑，无法发送消息')

    msg = ChatMessage()
    msg.msg_from = msg_from
    msg.to = to
    msg.message = content
    msg.read = False
    msg.created_at = time.time()

    db.session.add(msg)
    db.session.commit()

    return msg


def receive(uid, msg_from, new, offset=0, limit=10):
    if new:
        messages = ChatMessage.query.filter(and_(or_(and_(ChatMessage.msg_from==msg_from , ChatMessage.to==uid) , and_(ChatMessage.msg_from==uid , ChatMessage.to==msg_from)), (ChatMessage.read==False))).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    else:
        messages = ChatMessage.query.filter(or_(and_(ChatMessage.msg_from==msg_from , ChatMessage.to==uid), and_(ChatMessage.msg_from==uid , ChatMessage.to==msg_from))).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    for i in messages:
        i.read = True

    db.session.commit()

    return messages


def receive_all(uid, new, limit=10):
    if new:
        messages = ChatMessage.query.filter(ChatMessage.to==uid, ChatMessage.read==False).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    else:
        messages = ChatMessage.query.filter(ChatMessage.to==uid).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    for i in messages:
        i.read = True

    db.session.commit()

    return messages


def get_my_messages(later_than=0):
    uid = session['uid']
    messages = ChatMessage.query.filter(ChatMessage.msg_from == uid, ChatMessage.created_at >= later_than).all()
    
    return messages;