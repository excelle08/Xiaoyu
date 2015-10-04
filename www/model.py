# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from time import time
from api import to_json

db = SQLAlchemy()


def enum(**enums):
    return type('Enum', (), enums)

UserPermission = enum(Blocked=-1, Unvalidated=0, InProgress=1, Validated=2, Admin=3)
UserStatus = enum(Offline=0, Online=1, HideToFriends=2, HideToStrangers=3, HideToAll=4)


class Base():

    @property
    def json(self):
        return to_json(self, self.__class__)


class User(db.Model, Base):
    __tablename__ = 'user'
    uid = db.Column('uid', db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column('phonenum', db.String(32), nullable=False)
    password = db.Column('password', db.String(32), nullable=False)
    permission = db.Column('permission', db.Integer, nullable=False)
    online = db.Column('online', db.Integer, nullable=True)
    created_at = db.Column('created_at', db.Float, nullable=False)
    last_login = db.Column('last_login', db.Float, nullable=False)


Degree = enum(Unknown=0, Bachelor=1, Master=2, Phd=3)


class UserSchool(db.Model, Base):
    __tablename__ = 'user_school'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    school_name = db.Column('school_name', db.Text)
    degree = db.Column('degree', db.Integer)
    school_id = db.Column('school_id', db.Integer)
    school_province = db.Column('school_province', db.Integer)
    school_city = db.Column('school_city', db.Integer)
    auth_photo = db.Column('auth_photo', db.Text)
    auth_pass = db.Column('pass', db.Boolean)


class UserMeta(db.Model, Base):
    __tablename__ = 'user_meta'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    nickname = db.Column('nickname', db.String(32))
    realname = db.Column('realname', db.String(32))
    avatar = db.Column('avatar', db.Text)
    gender = db.Column('gender', db.Integer)
    age = db.Column('age', db.Integer)
    height = db.Column('height', db.Float)
    birthday = db.Column('birthday', db.Float)
    horoscope = db.Column('horoscope', db.Integer)
    hometown_province = db.Column('hometown_province', db.Integer)
    hometown_city = db.Column('hometown_city', db.Integer)
    hometown_addr = db.Column('hometown_addr', db.Text)
    workplace_province = db.Column('workplace_province', db.Integer)
    workplace_city = db.Column('workplace_city', db.Integer)
    workplace_addr = db.Column('workplace_addr', db.Text)
    contact = db.Column('contact', db.Text)
    motto = db.Column('motto', db.Text)
    show_contact = db.Column('show_contact', db.Boolean)
    show_name = db.Column('show_name', db.Boolean)


class UserExt(db.Model, Base):
    __tablename__ = 'user_ext'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    content = db.Column('content', db.Text)


class Wall(db.Model, Base):
    __tablename__ = 'wall'
    uid = db.Column('uid', db.Integer, primary_key=True, nullable=False)
    photos = db.Column('photos', db.Text)
    upvotes = db.Column('upvotes', db.Integer)
    wall_filter = db.Column('filter', db.Text)


class Photo(db.Model, Base):
    __tablename__ = 'photos'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    url = db.Column('url', db.Text)
    desc = db.Column('desc', db.Text)
    created_at = db.Column('created_at', db.Float)

Visibility = enum(All=0, FriendsOnly=1, Mutual=2)

class Tweet(db.Model, Base):
    __tablename__ = 'tweets'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    photos = db.Column('photos', db.Text)
    visibility = db.Column('visibility', db.Integer)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class Reply(db.Model, Base):
    __tablename__ = 'replies'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class Message(db.Model, Base):
    __tablename__ = 'messages'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class MessageReply(db.Model, Base):
    __tablename__ = 'msgreplies'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    visibility = db.Column('visibility', db.Integer)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class ChatMessage(db.Model, Base):
    __tablename__ = 'chatmsg'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    _from = db.Column('from', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)
    message = db.Column('message', db.Text)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class Friend(db.Model, Base):
    __tablename__ = 'friends'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)
    group = db.Column('group', db.Integer)
    agree = db.Column('agree', db.Boolean)


class FriendGroup(db.Model, Base):
    __tablename__ = 'friend_group'
    user = db.Column('user', db.Integer, primary_key=True)
    content = db.Column('content', db.Text)


class BlackList(db.Model, Base):
    __tablename__ = 'black_list'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('user', db.Integer, nullable=False)
    to = db.Column('to', db.Integer, nullable=False)


class Notification(db.Model, Base):
    __tablename__ = 'notification'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    content = db.Column('content', db.Text)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class AbuseReport(db.Model, Base):
    __tablename__ = 'abuse_report'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    _from = db.Column('from', db.Integer, nullable=False)
    target = db.Column('target', db.Integer, nullable=False)
    content = db.Column('content', db.Text)
    read = db.Column('read', db.Boolean)
    created_at = db.Column('created_at', db.Float)


class License(db.Model, Base):
    __tablename__ = 'license'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    content = db.Column('content', db.Text)


class Horoscope(db.Model, Base):
    __tablename__ = 'horoscope'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)
    desc = db.Column('desc', db.Text)


class Province(db.Model, Base):
    __tablename__ = 'province'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)


class City(db.Model, Base):
    __tablename__ = 'city'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    index = db.Column('index', db.Integer)
    province = db.Column('province', db.Integer, nullable=False)
    name = db.Column('name', db.Text)


class School(db.Model, Base):
    __tablename__ = 'school'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.Text)
    location = db.Column('location', db.Text)
    s_type = db.Column('type', db.Text)
    s_property = db.Column('properties', db.Text)
