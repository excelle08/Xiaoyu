# -*- coding: utf-8 -*-

from model import db, Message, MessageReply, User, Visibility
from flask import session
from api import APIError, friends
import time


def leave_message(target_user, content, visibility=Visibility.All):
    if not content:
        raise APIError('留言内容不能为空')
    if not User.query.filter_by(uid=target_user).first():
        raise APIError('指向的用户不存在')

    if friends.am_i_blocked(target_user):
        raise APIError('您被拉黑，无法留言。')

    message = Message()
    message.user = session['uid']
    message.target = target_user
    message.content = content
    message.visibility = visibility
    message.read = False
    message.created_at = time.time()

    db.session.add(message)
    db.session.commit()
    return message


def reply_message(target_message, content, visibility=Visibility.All):
    if not content:
        raise APIError('回复内容不能为空')
    msg = Message.query.filter(Message.id==target_message).first()
    if not msg:
        raise APIError('指向的留言不存在')

    reply = MessageReply()
    reply.user = session['uid']
    reply.target = target_message
    reply.content = content
    reply.visibility = visibility
    reply.read = False
    reply.created_at = time.time()

    db.session.add(reply)
    db.session.commit()
    return reply


def get_messages(uid, offset=0, limit=10, later_than=0):
    current_uid = session['uid']

    messages = Message.query.filter(Message.target==uid, Message.created_at>=later_than).all()
    items_to_remove = []

    for i in messages:
        if i.visibility == Visibility.Mutual and not (current_uid == i.user or current_uid == i.target):
            items_to_remove.append(i)
    messages = [item for item in messages if not item in items_to_remove]
    messages.sort(key=lambda msg: msg.created_at, reverse=True)
    return messages[offset: offset+limit]


def get_replies(target_reply, offset=0, limit=10, later_than=0):
    current_uid = session['uid']

    message = Message.query.filter_by(id=target_reply).first()
    replies = MessageReply.query.filter(MessageReply.target==target_reply, MessageReply.created_at>=later_than).all()
    
    items_to_remove = []
    for i in replies:
        if i.visibility == Visibility.Mutual and not (current_uid == message.user or current_uid == i.user):
            items_to_remove.append(i)
    replies = [item for item in replies if not item in items_to_remove]
    replies.sort(key=lambda reply: reply.created_at)

    return replies[offset: offset+limit]


def remove_message(id):
    current_uid = session['uid']

    message = Message.query.filter_by(id=id).first()
    if not (current_uid == message.user or current_uid == message.target):
        raise APIError('您没有权限来删除此留言')

    replies = MessageReply.query.filter_by(target=id).all()
    for reply in replies:
        db.session.delete(reply)

    db.session.delete(message)
    db.session.commit()
    return {"id": id}


def remove_reply(id):
    current_uid = session['uid']

    reply = MessageReply.query.filter_by(id=id).first()
    message = Message.query.filter_by(id=reply.target).first()
    if not (current_uid == reply.user or current_uid == message.user):
        raise APIError('您没有权限来删除此回复')

    db.session.delete(reply)
    db.session.commit()

    return {"id": id}
