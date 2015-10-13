# -*- coding: utf-8 -*-

from model import User, UserPermission, UserStatus, db
from model import UserSchool, UserMeta, UserExt, Wall, FriendGroup, Friend, BlackList, School
from model import Tweet
from flask import session
from api import APIError
from api.wall import filter_default, filter_users
import re, json, requests, random, time, hashlib

_PHONENUM = re.compile(r'^[0-9\-]+$')
_MD5 = re.compile(r'^[0-9A-Fa-f]{32}$')
sms_apikey = 'c6745a3a14ab7d3227a7adf1a2800dbc'
sms_url = 'http://yunpian.com/v1/sms/send.json'


def send_message(phone):
    code = generate_vcode()
    post_data = {
        "apikey" : sms_apikey,
        "mobile" : phone,
        "text" : "【云片网】您的验证码是%s" % code
    }
    resp = requests.post(sms_url, data=post_data)
    return resp.content


def generate_vcode():
    rand_char = [ chr(random.randint(48, 58)) for i in range(0,4) ]
    rand_char = str.join('', rand_char)
    session['vcode'] = rand_char
    return rand_char


def user_register(phone, password, vcode):
    if not _PHONENUM.match(phone.strip()):
        raise APIError('请输入正确的手机号码')
    if vcode.lower() != session['vcode']:
        raise APIError('短信验证码错误')
    exist = User.query.filter_by(phone=phone.strip()).first()
    if exist:
        raise APIError('该手机号已经注册过')

    user = User()
    user.phone = phone.strip()
    user.password = hashlib.md5(password.strip()).hexdigest()
    user.permission = UserPermission.Unvalidated
    user.created_at = time.time()
    user.last_login = time.time()
    user.online = UserStatus.Online
    db.session.add(user)
    db.session.commit()

    school = UserSchool()
    school.uid = user.uid

    meta = UserMeta()
    meta.uid = user.uid
    meta.avatar = 'static/images/default_avatar.png'
    meta.small_avatar = '{}'

    ext = UserExt()
    ext.uid = user.uid
    ext.content = '{}'

    wall = Wall()
    wall.uid = user.uid
    wall.wall_filter = json.dumps(filter_default)
    wall.created_at = time.time()
    wall.published = False

    fgroup = FriendGroup()
    fgroup.user = user.uid
    fgroup.content = json.dumps(['好友', '密友'])

    db.session.add(school)
    db.session.add(meta)
    db.session.add(ext)
    db.session.add(wall)
    db.session.add(fgroup)
    db.session.commit()
    del session['vcode']

    # login
    session['uid'] = user.uid
    session['phone'] = phone.strip()
    session['password'] = user.password
    return user


def user_login(phone, password, remember):
    if not _PHONENUM.match(phone.strip()):
        raise APIError('请输入正确的手机号码')
    user = User.query.filter_by(phone=phone.strip()).first()
    if not user:
        raise APIError('该用户不存在或密码错误')
    if user.password.lower() != hashlib.md5(password.strip()).hexdigest().lower():
        raise APIError('该用户不存在或密码错误')

    user.last_login = time.time()
    user.online = UserStatus.Online

    if remember:
        session.permanent = True
    session['uid'] = user.uid
    session['phone'] = phone.strip()
    session['password'] = user.password
    return user


def validate_user(uid, phone, password):
    user = User.query.filter_by(uid=uid).first()
    if not user:
        print  'User does not exist'
        return False

    if not phone == user.phone:
        print 'Phone does not match'
        print phone
        print user.phone
        return False

    if not password == user.password:
        print password
        print user.password
        print 'pwd does not match'
        return False

    return True


def user_logout():
    try:
        user = User.query.filter_by(phone=session['phone']).first()
        if not user:
            return
        user.online = UserStatus.Offline
        db.session.commit()
        del session['phone']
        del session['password']
        del session['uid']
    except KeyError, e:
        raise APIError(e.message)


def get_online_users(offset=0, limit=10):
    users = User.query.filter_by(online=UserStatus.Online).offset(offset).limit(limit).all()
    filters = set(filter_users(session['uid']))
    onlines = set([UserMeta.query.filter_by(uid=item.uid).first() for item in users])
    res = set.intersection(filters, onlines)
    return list(res)


def get_recent_logins(offset=0, limit=10):
    users = User.query.order_by(User.last_login.desc()).offset(offset).limit(limit).all()
    recents = set([ UserMeta.query.filter_by(uid=item.uid).first() for item in users ])
    filters = set(filter_users(session['uid']))
    res = set.intersection(filters, recents)
    return list(res)


def get_hot_users(offset=0, limit=10):
    walls = Wall.query.order_by(Wall.upvotes.desc()).offset(offset).limit(limit).all()
    hots = set([ UserMeta.query.filter_by(uid=item.uid).first() for item in walls ])
    filters = set(filter_users(session['uid']))
    res = set.intersection(filters, hots)
    return list(res)


def get_user(uid):
    return User.query.filter_by(uid=uid).first()


def get_user_meta(uid):
    return UserMeta.query.filter_by(uid=uid).first()


def get_user_extension(uid):
    return json.loads(UserExt.query.filter_by(uid=uid).first().content)


def get_user_friend_groups(uid):
    return json.loads(FriendGroup.query.filter_by(uid=uid).first().content)


def get_friends(uid):
    return Friend.query.filter_by(user=uid).all()


def get_blacklist(uid):
    return BlackList.query.filter_by(user=uid).all()


def get_user_school(uid):
    return UserSchool.query.filter_by(uid=uid).first()


def set_user_school(uid, school_id, degree, auth_photo):
    school = UserSchool()
    s = School.query.filter_by(id=school_id)
    if not s:
        raise APIError('指定的学校不存在')
    school.uid = uid
    school.school_name = s.name
    school.degree = degree
    school.school_id = school_id
    school.auth_photo = auth_photo
    school.auth_pass = False
    user = User.query.filter_by(uid=uid)
    user.permission = UserPermission.InProgress

    db.session.add(school)
    db.session.commit()
    return school


def pass_user_school(uid):
    school = UserSchool.query.filter_by(uid=uid).first()
    school.auth_pass = True
    user = User.query.filter_by(uid=uid).first()
    user.permission = UserPermission.Validated

    db.session.commit()
    return school


def set_user_meta(uid, args):
    try:
        umeta = UserMeta.query.filter_by(uid=uid).first()
        for key, value in args.iteritems():
            # Skip empty items
            if not value:
                continue
            umeta.__setattr__(key, value)
        db.session.commit()
        return umeta
    except KeyError, e:
        raise APIError(e.message)


def set_user_ext(uid, args):
    uext = UserExt.query.filter_by(uid=uid).first()
    uext.content = json.dumps(args)
    db.session.commit()
    return uext


def set_user_password(uid, new, new_2, vcode):
    try:
        user = User.query.filter_by(uid=uid).first()
        if not vcode == session['vcode']:
            raise APIError('短信验证码错误')
        if not _MD5.match(new):
            raise APIError('密码Hash值格式不正确')
        if not new.strip().lower() == new_2.strip().lower():
            raise APIError('两次密码不一样')
        user.password = new
        db.session.commit()
        del session['vcode']
        user_logout()
    except KeyError, e:
        raise APIError(e.message)


def set_user_login_state(uid, state):
    u = User.query.filter_by(uid=uid).first()
    u.online = state

    db.session.commit()
    return u
