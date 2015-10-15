# -*- coding: utf-8 -*-

from model import db
from model import ChatMessage, Friend
from api import APIError
import api.friends
import time


def send(_from, to, content):
    f = Friend.query.filter(Friend.user==_from, Friend.to==to).first()
    if not f:
        raise APIError('非好友关系不能发送信息~')
    bk = BlackList.query.filter()

    if api.friends.am_i_blocked(to):
        raise APIError('您被拉黑，无法发送消息')

    msg = ChatMessage()
    msg._from = _from
    msg.to = to
    msg.message = content
    msg.read = False
    msg.created_at = time.time()

    db.session.add(msg)
    db.session.commit()

    return msg


def receive(uid, _from):
    messages = ChatMessage.query.filter(ChatMessage._from==_from, ChatMessage.to==uid, ChatMessage.read==False).order_by(ChatMessage.created_at.desc()).all()
    for i in messages:
        i.read = True

    db.session.commit()
    return messages


def receive_all(uid):
    messages = ChatMessage.query.filter(ChatMessage.to==uid, ChatMessage.read==False).order_by(ChatMessage.created_at.desc()).all()
    for i in messages:
        i.read = True

    db.session.commit()
    return messages