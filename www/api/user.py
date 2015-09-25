# -*- coding: utf-8 -*-

from model import User, UserPermission, db
from model import UserSchool, UserExt, Wall, FriendGroup
from flask import session
from api import APIError, APIValueError
import re, json

_PHONENUM = re.compile(r'^[0-9\-]+$')
_MD5 = re.compile(r'^[0-9A-Fa-f]{32}$')


def send_message(captcha):
    pass


def user_register(phone, password, vcode):
    if not _PHONENUM.match(phone.strip()):
        raise APIError('请输入正确的手机号码')
    if not _MD5.match(password.strip().lower()):
        raise APIError('密码Hash值格式不正确')
    if vcode.lower() != session['vcode']:
        raise APIError('短信验证码错误')
    exist = User.query.filter_by(phone=phone.strip()).first()
    if exist:
        raise APIError('该手机号已经注册过')

    user = User()
    user.phone = phone.strip()
    user.password = password.strip().lower()
    user.permission = UserPermission.Unvalidated
    db.session.add(user)
    db.session.commit()

    school = UserSchool()
    school.uid = user.uid

    meta = UserMeta()
    meta.uid = user.uid

    ext = UserExt()
    ext.uid = user.uid
    ext.content = '{}'

    wall = Wall()
    wall.uid = user.uid

    fgroup = FriendGroup()
    fgroup.uid = user.uid
    fgroup.content = json.dumps({'1': '好友', '2': '密友'})

    db.session.add(school)
    db.session.add(meta)
    db.session.add(ext)
    db.session.add(wall)
    db.session.add(fgroup)
    db.session.commit()

    return user


def user_login(phone, password, remember):
    if not _PHONENUM.match(phone.strip()):
        raise APIError('请输入正确的手机号码')
    if not _MD5.match(password.strip().lower()):
        raise APIError('密码Hash值格式不正确')
    user = User.query.filter_by(phone=phone.strip()).first()
    if not user:
        raise APIError('该用户不存在或密码错误')
    if user.password.lower() != password.strip().lower():
        raise APIError('该用户不存在或密码错误')

    if remember:
        session.permanent = True
    session['phone'] = phone.strip()
    session['password'] = password.strip().lower()
    return user



