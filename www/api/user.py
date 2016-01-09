# -*- coding: utf-8 -*-

from model import User, UserPermission, UserStatus, db
from model import UserSchool, UserMeta, UserExt, Wall, FriendGroup, Friend, BlackList, School
from model import Tweet
from flask import session
from api import APIError
from api.wall import filter_default, filter_users
import re, json, requests, random, time, hashlib
from sqlalchemy import or_, and_

_PHONENUM = re.compile(r'^[0-9\-]+$')
_MD5 = re.compile(r'^[0-9A-Fa-f]{32}$')
sms_appkey = '23279977'
sms_secret = 'fabfae89de7206ff74d0eb43d223dbbf'


def send_message(phone, sms_type):
    import top.api
    req=top.api.AlibabaAliqinFcSmsNumSendRequest()
    req.set_app_info(top.appinfo(sms_appkey,sms_secret))
    req.extend="123456"
    req.sms_type="normal"
    req.sms_param= json.dumps({'code' : generate_vcode(), 'product' : '校遇'})
    req.rec_num=phone
    if sms_type == 0:
        req.sms_template_code="SMS_3005317"
        req.sms_free_sign_name='注册验证'
    elif sms_type == 1:
        req.sms_template_code="SMS_3005315"
        req.sms_free_sign_name='变更验证'
    try:
        resp= req.getResponse()
        session['vcode_phone'] = phone
    except Exception:
        pass
    return '{"status":"success"}'


def generate_vcode():
    rand_char = [ chr(random.randint(48, 58)) for i in range(0,4) ]
    rand_char = str.join('', rand_char)
    rand_char = rand_char.replace(':', '0')
    session['vcode'] = rand_char
    return rand_char


def user_register(phone, password, vcode, autologin=True):
    if not _PHONENUM.match(phone.strip()):
        raise APIError('请输入正确的手机号码')
    if (not 'vcode' in session) or (not 'vcode_phone' in session):
        raise APIError('短信验证码错误')
    if vcode.lower() != session['vcode'] or phone != session['vcode_phone']:
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
    school.auth_pass = False

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
    fgroup.content = json.dumps(['好友', '密友', '陌生人'])

    db.session.add(school)
    db.session.add(meta)
    db.session.add(ext)
    db.session.add(wall)
    db.session.add(fgroup)
    db.session.commit()
    del session['vcode']
    del session['vcode_phone']

    # login
    if autologin:
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
    if user.online != 3 and user.online != 4:
        user.online = UserStatus.Online
    db.session.commit()

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
        if user.online != 3 and user.online != 4 and user.online != 2:
            user.online = UserStatus.Offline
        db.session.commit()
        del session['phone']
        del session['password']
        del session['uid']
    except KeyError, e:
        raise APIError(e.message)

def get_visible_online_users():
    friend_list = get_friends(session['uid'])
    visible_friends = []
    for friend in friend_list:
        friend_info = User.query.filter_by(uid=friend.to).first()
        if friend_info.online == UserStatus.HideToStrangers:
            visible_friends.append(UserMeta.query.filter_by(uid=friend_info.uid).first())
    friend_uid_list = [friend.to for friend in friend_list]
    hide_to_friends_list = User.query.filter_by(online=UserStatus.HideToFriends).all()
    for user in hide_to_friends_list:
        if (not user.uid in friend_uid_list):
            visible_friends.append(UserMeta.query.filter_by(uid=user.uid).first())
    return visible_friends


def get_online_users(offset=0, limit=10):
    users = User.query.filter_by(online=UserStatus.Online).all()
    filters = filter_users(session['uid'])
    onlines = [UserMeta.query.filter_by(uid=item.uid).first() for item in users]
    res = [user for user in onlines if user in filters]
    res.extend(get_visible_online_users())
    res = res[int(offset):int(limit)]
    res = [user.dict for user in res]
    for user_meta in res:
        try:
            user_meta['permission'] = User.query.filter_by(uid=user_meta['uid']).first().permission
        except Exception:
            continue
    return res


def get_recent_logins(offset=0, limit=10):
    users = User.query.filter(User.online == UserStatus.Offline).order_by(User.last_login.desc()).all()
    recents = [ UserMeta.query.filter_by(uid=item.uid).first() for item in users ]
    filters = filter_users(session['uid'])
    res = [user for user in recents if user in filters]
    #visible_online_users = get_visible_online_users()
    #res = [user for user in res if not user in visible_online_users]
    res = res[int(offset):int(limit)]
    res = [user.dict for user in res]
    for user_meta in res:
        try:
            user_meta['permission'] = User.query.filter_by(uid=user_meta['uid']).first().permission
        except Exception:
            continue
    return res


def get_hot_users(offset=0, limit=10):
    walls = Wall.query.order_by(Wall.upvotes.desc()).offset(offset).all()
    hots = [ UserMeta.query.filter_by(uid=item.uid).first() for item in walls ]
    filters = filter_users(session['uid'], True)
    res = [user for user in hots if user in filters]
    res = res[int(offset):int(limit)]
    res = [user.dict for user in res]
    for user_meta in res:
        try:
            user_meta['permission'] = User.query.filter_by(uid=user_meta['uid']).first().permission
        except Exception:
            continue
    return res


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


def set_user_school(uid, school_id, major, degree, auth_photo):
    school = UserSchool.query.filter_by(uid=uid).first()
    s = School.query.filter_by(id=school_id).first()
    if not s:
        raise APIError('指定的学校不存在')
    school.school_name = s.name
    school.major = major
    school.degree = degree
    school.school_id = school_id
    school.auth_photo = auth_photo
    school.auth_pass = False
    user = User.query.filter_by(uid=uid).first()
    user.permission = UserPermission.InProgress

    db.session.commit()
    return school


def pass_user_school(uid):
    school = UserSchool.query.filter_by(uid=uid).first()
    if not school:
        raise APIError('不存在此用户')
    school.auth_pass = True
    user = User.query.filter_by(uid=uid).first()
    user.permission = UserPermission.Validated

    db.session.commit()
    return school


def set_user_meta(uid, args):
    try:
        umeta = UserMeta.query.filter_by(uid=uid).first()
        if not umeta:
            umeta = UserMeta()

        for key, value in args.iteritems():
            # Skip empty items
            if not value:
                continue
            #print 'key=' + key + ';value=' + value
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


def set_user_password(phone, new, vcode):
    try:
        user = User.query.filter_by(phone=phone.strip()).first()
        if not user:
            raise APIError('该手机号未被注册')
        if (not 'vcode' in session) or (not 'vcode_phone' in session):
            raise APIError('短信验证码错误')
        if not vcode == session['vcode'] or phone != session['vcode_phone']:
            raise APIError('短信验证码错误')
        user.password = hashlib.md5(new.strip()).hexdigest()
        db.session.commit()
        del session['vcode']
        del session['vcode_phone']
        return {'status':'success'}
    except KeyError, e:
        raise APIError(e.message)


def set_user_login_state(uid, state):
    u = User.query.filter_by(uid=uid).first()
    u.online = state

    db.session.commit()
    return u

def update_user_age():
    print('Running user age check')
    all_users = UserMeta.query.all()
    for user_meta in all_users:
        if (user_meta.birthday == None):
            continue
        from datetime import datetime
        user_meta.age = int(calculate_age(datetime.fromtimestamp(user_meta.birthday)))

    expired_login_users = User.query.filter(and_(User.last_login < (time.time() - 5*60), or_(User.online == 1, User.online == 2, User.online == 3))).all()
    for user in expired_login_users:
        user.online = 0

    db.session.commit()
    return {'status':200}

def calculate_age(born):
    from datetime import date
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
