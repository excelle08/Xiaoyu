from model import db
from model import ChatMessage, Friend
from api import APIError
import time


def send(_from, to, content):
    f = Friend.query.filter_by(user=_from, to=to).first()
    if not f:
        raise APIError('非好友关系不能发送信息~')

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
    messages = ChatMessage.query.filter_by(_from=_from, to=uid, read=False).ordered_by(ChatMessage.created_at.desc()).all()
    for i in messages:
        i.read = True

    db.session.commit()
    return messages


def receive_all(uid):
    messages = ChatMessage.query.filter_by(to=uid, read=False).ordered_by(ChatMessage.created_at.desc()).all()
    for i in messages:
        i.read = True

    db.session.commit()
    return messages