# -*- coding: utf-8 -*-

from flask import Flask, Response
from flask import jsonify, session, request
from flask import render_template, make_response
from flask import redirect, url_for
from api import APIError, check_admin
from model import db, UserPermission
import api.admin
import api.common, api.user, api.tweets, api.message, api.friends
import api.photo, api.album, api.wall, api.chat, api.notify, api.abuse_report, api.statistics
import json, re, time

app = Flask(__name__)
db.init_app(app)

nopriv_allowed = [
    '/static/.*',
    '/login',
    '/reg',
    '/api/common/.*',
    '/api/user/verify',
    '/api/user/login',
    '/api/user/password/edit',
    '/api/user/cron',
    '/api/register',
    '/api/test/.*',
    '/test.*',
    '/api/ua',
    '/api/user/autologin'
]

blocked_allowed = [
    '/static/.*',
    '/changepass',
    '/home',
    '/',
    '/edit',
    '/api/user.*',
    '/api/common/.*',
    '/api/notification.*',
    '/api/test/.*',
    '/test.*'
]


def render_html(filename):
    path = 'templates/' + filename
    with open(path, 'r') as f:
        html_str = f.read()

    return Response(html_str, mimetype='text/html')


def return_json(data, default=None):
    return Response(json.dumps(data, default=default), mimetype='text/json')


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


#  ------------Permission control, Interceptor---------------
@app.before_request
def admin_interceptor():
    if '/admin' in request.path:  
        uid = session['uid'] if 'uid' in session else None
        if not uid:
            return redirect(url_for('.index'))

        if not check_admin():
            return redirect(url_for('.index'))


@app.before_request
def user_interceptor():
    global nopriv_allowed

    auth_flag = False

    if 'uid' in session and 'phone' in session and 'password' in session:
        uid = session['uid']
        phone = session['phone']
        password = session['password']
        if api.user.validate_user(uid, phone, password):
            auth_flag = True

    for item in nopriv_allowed:
        regex = '^' + item + '$'
        if re.match(regex, request.path):
            auth_flag = True
            break

    if not auth_flag:
        return return_json({'error':'你未登录'})


@app.before_request
def blockeds_interceptor():
    global blocked_allowed

    auth_flag = False

    if 'uid' in session:
        user = api.user.get_user(session['uid'])
        if not user:
            return
        if user.permission == UserPermission.Blocked:
            for item in blocked_allowed:
                regex = '^' + item + '$'
                if re.match(regex, request.path):
                    auth_flag = True
                    break
        else:
            auth_flag = True

        if not auth_flag:
            raise APIError('您被封禁，无法使用此功能。')

#  ---------------Front-end view rendering route--------------
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_html('index.html')


@app.route('/reg', methods=['GET', 'POST'])
def register():
    return render_html('reg.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_html('login.html')


@app.route('/changepass', methods=['GET', 'POST'])
def changepass():
    return render_html('changepass.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_html('me.html')


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    if 'uid' in request.args:
        return render_html('others.html')

    return render_html('friends.html')


@app.route('/reply', methods=['GET', 'POST'])
def reply():
    return render_html('reply.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_html('reply.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit_info():
    return render_html('homepage.html')


@app.route('/friendwall', methods=['GET', 'POST'])
def guestwall():
    return render_html('fwall.html')


@app.route('/mywall', methods=['GET', 'POST'])
def mywall():
    return render_html('mywall.html')


@app.route('/compile', methods=['GET', 'POST'])
def compile():
    return render_html('compile.html')


@app.route('/publish', methods=['GET', 'POST'])
def publish_tweet():
    return render_html('publish.html')


@app.route('/message', methods=['GET', 'POST'])
def message_center():
    return render_html('message.html')


@app.route('/notification', methods=['GET', 'POST'])
def notification():
    return render_html('notification.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_publish_nofitication():
    return render_template('admin/index.html')


@app.route('/admin/notification', methods=['GET', 'POST'])
def admin_notifications():
    return render_template('admin/notification.html')


@app.route('/admin/stat', methods=['GET', 'POST'])
def admin_stat():
    return render_template('admin/stat.html')


@app.route('/admin/user', methods=['GET', 'POST'])
def admin_user():
    return render_template('admin/user.html')


@app.route('/admin/school', methods=['GET', 'POST'])
def admin_school():
    return render_template('admin/school.html')


@app.route('/admin/abusereport', methods=['GET', 'POST'])
def admin_abuse_report():
    return render_template('admin/abusereport.html')


@app.route('/admin/message', methods=['GET', 'POST'])
def admin_global_message():
    return render_template('admin/message.html')


### This is for test.
### Will be removed in production mode

@app.route('/test/api/register', methods=['GET', 'POST'])
def test_user_register():
    phone = request.form['phone']
    password = request.form['password']
    user = api.user.test_user_register(phone, password)
    return user.json

@app.route('/api/test/verify', methods=['POST'])
def test_verify():
    phone = request.form['phone']
    session['vcode_phone'] = phone
    return return_json({"vcode": api.user.generate_vcode()})

### end


# ---------------User-related backend API---------------------
@app.route('/api/user/verify', methods=['POST'])
def api_send_verification_sms():
    try:
        phone = request.form['phone']
        sms_type = int(request.form['type']) if 'type' in request.form else 0
        return Response(api.user.send_message(phone, sms_type), mimetype="text/json")
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/register', methods=['POST'])
def api_user_register():
    try:
        phone = request.form['phone']
        password = request.form['password']
        vcode = request.form['vcode']
        
        user = api.user.user_register(phone, password, vcode)
        return return_json({"uid": user.uid, "created_at": user.created_at})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/login', methods=['POST'])
def api_user_login():
    try:
        phone = request.form['phone']
        password = request.form['password']
        remember = request.form['remember'] if 'remember' in request.form else False

        user = api.user.user_login(phone, password, remember)
        return return_json({"uid": user.uid})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/logout', methods=['GET', 'POST'])
def api_user_logout():
    api.user.user_logout()
    return return_json({'status':200})


@app.route('/api/user/onlines', methods=['GET', 'POST'])
def api_get_online_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_online_users(offset, limit))


@app.route('/api/user/hot', methods=['GET', 'POST'])
def api_get_hot_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_hot_users(offset, limit))


@app.route('/api/user/recent_login', methods=['GET', 'POST'])
def api_get_recent_logins():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_recent_logins(offset, limit))


@app.route('/api/user', methods=['GET', 'POST'])
def api_get_user():
    try:
        uid = session['uid']
        u = api.user.get_user(uid)
        return Response(u.json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/online', methods=['GET', 'POST'])
def api_set_user_online_state():
    try:
        uid = session['uid']
        status = request.args['status']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.user.set_user_login_state(uid, status).json, mimetype='text/json')


@app.route('/api/user/meta', methods=['GET', 'POST'])
def api_get_user_meta():
    from model import User
    uid = request.args['uid'].strip() if "uid" in request.args else session['uid']
    userMeta = json.loads(api.user.get_user_meta(uid).json)
    userMeta['online'] = User.query.filter_by(uid=uid).first().online
    userMeta['last_login'] = User.query.filter_by(uid=uid).first().last_login
    userMeta['permission'] = User.query.filter_by(uid=uid).first().permission
    return return_json(userMeta)


@app.route('/api/user/ext', methods=['GET', 'POST'])
def api_get_user_ext():
    uid = request.args['uid'].strip() if "uid" in request.args else session['uid']
    return return_json(api.user.get_user_extension(uid))


@app.route('/api/user/meta/edit', methods=['POST'])
def api_edit_user_meta():
    uid = session['uid']
    args = request.form
    return Response(api.user.set_user_meta(uid, args).json, mimetype='text/json')


@app.route('/api/user/ext/edit', methods=['POST'])
def api_edit_user_ext():
    uid = session['uid']
    args = request.form
    return Response(api.user.set_user_ext(uid, args).json, mimetype='text/json')


@app.route('/api/user/school/edit', methods=['POST'])
def api_edit_user_school():
    try:
        uid = session['uid']
        school_id = request.form['school']
        degree = request.form['degree']
        major = request.form['major']
        photo = request.form['photo']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.user.set_user_school(uid, school_id, major, degree, photo).json, mimetype='text/json')


@app.route('/api/user/school/get', methods=['GET'])
def api_get_user_school():
    uid = int(request.args['uid']) if 'uid' in request.args else session['uid']
    user_school = json.loads(api.user.get_user_school(uid).json)
    if not check_admin() and uid != session['uid']:
        user_school['auth_photo'] = ''
    return jsonify(user_school)


@app.route('/api/user/password/edit', methods=['POST'])
def api_edit_password():
    phone = request.form['phone']
    new = request.form['new']
    vcode = request.form['vcode']
    return jsonify(api.user.set_user_password(phone, new, vcode))

@app.route('/api/user/cron', methods=['GET'])
def api_user_cron_tasks():
    return return_json(api.user.update_user_age())


#    ------------------FRIENDS----------------
@app.route('/api/user/friends/add', methods=['GET', 'POST'])
def api_add_friend():
    try:
        target = request.args['target'].strip()
        group = request.args['group'].strip() if 'group' in request.args else 0
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.friends.add_friends(target, group).json, mimetype='text/json')

@app.route('/api/user/friends', methods=['GET', 'POST'])
def api_get_friends():
    return return_json(api.friends.get_friends(), default=lambda obj: obj.dict)


@app.route('/api/user/friends/groups', methods=['GET', 'POST'])
def api_get_friends_group():
    return return_json(api.friends.get_friend_groups())


@app.route('/api/user/friends/groups/add', methods=['GET', 'POST'])
def api_add_friends_group():
    try:
        title = request.args['title'].strip()
        return Response(api.friends.add_friend_group(title).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/groups/delete', methods=['GET', 'POST'])
def api_delete_friends_group():
    try:
        g_id = request.args['id'].strip()
        return Response(api.friends.delete_friend_group(g_id).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/groups/modify', methods=['GET', 'POST'])
def api_modify_friend_group():
    try:
        g_id = request.args['id'].strip()
        title = request.args['title'].strip()
        return Response(api.friends.rename_friend_group(g_id, title).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/agree', methods=['GET', 'POST'])
def api_agree_friends_request():
    try:
        req_id = request.args['req_id'].strip()
        group = request.args['group'] if 'group' in request.args else 0
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.friends.agree_friend(req_id, group).json, mimetype='text/json')


@app.route('/api/user/friends/reject', methods=['GET', 'POST'])
def api_reject_friend_request():
    try:
        id = request.args['id'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.friends.reject_friend(id))


@app.route('/api/user/friends/get_requests', methods=['GET', 'POST'])
def api_retrieve_friend_request():
    return return_json(api.friends.get_friend_requests(), default=lambda obj: obj.dict)


@app.route('/api/user/friends/transgroup', methods=['GET', 'POST'])
def api_trans_friend_group():
    try:
        friend_id = request.args['friend_id'].strip()
        to_group = request.args['to_group'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.friends.trans_friend(friend_id, to_group).json, mimetype='text/json')


@app.route('/api/user/friends/delete', methods=['GET', 'POST'])
def api_delete_friend():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.friends.delete_friend(uid))


@app.route('/api/user/blacklist/add', methods=['GET', 'POST'])
def api_add_to_blacklist():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.friends.add_to_blacklist(uid).json, mimetype='text/json')


@app.route('/api/user/blacklist/get', methods=['GET', 'POST'])
def api_get_blacklist():
    return return_json([json.loads(user.json) for user in api.friends.get_blacklist()])


@app.route('/api/user/blacklist/delete', methods=['GET', 'POST'])
def api_delete_from_blacklist():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.friends.remove_from_blacklist(uid))


#    -------------W A L L---------------
@app.route('/api/wall/go', methods=['GET', 'POST'])
def api_go_to_wall():
    return Response(api.wall.user_upwall().json, mimetype='text/json')


@app.route('/api/wall/get', methods=['GET', 'POST'])
def api_get_wall():
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return Response(api.wall.get_user_wall(uid).json, mimetype='text/json')


@app.route('/api/wall/cancel', methods=['GET', 'POST'])
def api_delete_wall():
    uid = session['uid']
    return Response(json.dumps(api.wall.cancel_wall(uid)), mimetype='text/json')


@app.route('/api/wall/edit_filter', methods=['POST'])
def api_edit_filter():
    uid = session['uid']
    return Response(api.wall.set_my_filter(uid, request.form).json, mimetype='text/json')


@app.route('/api/wall/edit_wall', methods=['POST'])
def api_edit_wall():
    uid = session['uid']
    cover = request.form['cover']
    title = request.form['title']
    content = request.form['content']
    return Response(api.wall.edit_wall(uid, cover, title, content).json, mimetype='text/json')


@app.route('/api/wall/upvote', methods=['GET', 'POST'])
def api_upvote_user():
    try:
        uid = request.args['uid'] if 'uid' in request.args else session['uid']
    except KeyError, e:
        raise APIError(e.message)
    return Response(api.wall.upvote_user(uid).json, mimetype='text/json')


@app.route('/api/wall/upvote/new', methods=['GET', 'POST'])
def api_get_my_new_upvotes():
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return return_json(api.wall.get_new_upvotes(uid), default=lambda obj: obj.dict)


@app.route('/api/wall/upvote/all', methods=['GET', 'POST'])
def api_get_all_upvotes():
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return return_json(api.wall.get_all_my_upvotes(uid), default=lambda obj: obj.dict)


@app.route('/api/wall/guestwall', methods=['GET', 'POST'])
def api_get_guest_wall():
    uid = session['uid']
    guests = api.wall.get_guest_wall_items(uid)
    return return_json(guests, default=lambda obj: obj.dict)


#  -------- Tweet system -----------
@app.route('/api/tweet/add', methods=['POST'])
def api_add_tweet():
    try:
        content = request.form['content']
        photos = request.form.getlist('photos[]')
    except KeyError, e:
        raise APIError(e.message)
    visibility = request.form['visibility'] if 'visibility' in request.form else 0
    return Response(api.tweets.write_tweet(content, photos, visibility).json, mimetype='text/json')


@app.route('/api/tweet/getall', methods=['GET', 'POST'])
def api_get_friends_tweets():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.tweets.get_friends_tweets(int(offset), int(limit), later_than), default=lambda obj: obj.dict)


@app.route('/api/tweet/user', methods=['GET', 'POST'])
def api_get_ones_tweets():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.tweets.get_users_tweets(uid, int(offset), int(limit), later_than), default=lambda obj:obj.dict)


@app.route('/api/tweet/reply', methods=['POST'])
def api_reply_tweet():
    try:
        target_tweet_id = request.form['target'].strip()
        content = request.form['content'].strip()
        visibility = request.form['visibility'].strip() if 'visibility' in request.form else 0
        return Response(api.tweets.reply(target_tweet_id, content, visibility).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/tweet/reply/get', methods=['GET', 'POST'])
def api_reply_get():
    try:
        tweet_id = request.args['id'].strip()
    except KeyError, e:
        raise APIError(e.message)
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.tweets.get_replies(tweet_id, offset, limit, later_than), default=lambda obj: obj.dict)


@app.route('/api/tweet/delete', methods=['GET', 'POST'])
def api_tweet_delete():
    try:
        tweet_id = request.args['id'].strip()
        return return_json(api.tweets.remove_tweet(tweet_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/tweet/reply/delete', methods=['GET', 'POST'])
def api_reply_delete():
    try:
        reply_id = request.args['id'].strip()
        return return_json(api.tweets.remove_reply(reply_id))
    except KeyError, e:
        raise APIError(e.message)


# ------------Photo system------------------
@app.route('/api/photo/upload', methods=['POST'])
def api_upload_photo():
    try:
        photo = request.files['photo']
        url = api.photo.upload_photo(photo, request.form)
        return json.dumps({'url': url})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/album/upload', methods=['POST'])
def api_upload_to_album():
    try:
        photo = request.files['photo']
        desc = request.form['desc'] if 'desc' in request.form else ''
        return api.album.upload_photo(photo, desc, request.args).json
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/album/get', methods=['GET', 'POST'])
def api_get_album_photos():
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return return_json( api.album.get_all_photos(uid), default=lambda obj: obj.dict)


@app.route('/api/album/delete', methods=['GET', 'POST'])
def api_remove_photo():
    try:
        photo_id = request.args['id'].strip()
        return return_json(api.album.remove_photo(photo_id))
    except KeyError, e:
        raise APIError(e.message)


# ---------------Message-------------------
@app.route('/api/message/add', methods=['POST'])
def api_message_add():
    try:
        target_uid = request.form['uid']
        content = request.form['content']
        visibility = request.form['visibility'] if 'visibility' in request.form else 0
        return Response(api.message.leave_message(target_uid, content, visibility).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/reply/add', methods=['POST'])
def api_message_reply():
    try:
        message_id = request.form['id']
        content = request.form['content'] 
        visibility = request.form['visibility'] if 'visibility' in request.form else 0
        return Response(api.message.reply_message(message_id, content, visibility).json, mimetype='text/json')
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/get', methods=['GET', 'POST'])
def api_message_get():
    uid = request.args['uid'].strip() if 'uid' in request.args else session['uid']
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.message.get_messages(uid, int(offset), int(limit), later_than), default=lambda obj: obj.dict)


@app.route('/api/message/reply/get', methods=['GET', 'POST'])
def api_message_reply_get():
    try:
        message_id = request.args['id']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.message.get_replies(message_id, int(offset), int(limit), later_than), default=lambda obj: obj.dict)


@app.route('/api/message/delete', methods=['GET', 'POST'])
def api_message_delete():
    try:
        message_id = request.args['id']
        return return_json(api.message.remove_message(message_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/reply/delete', methods=['GET', 'POST'])
def api_message_Reply_delete():
    try:
        reply_id = request.args['id']
        return return_json(api.message.remove_reply(reply_id))
    except KeyError, e:
        raise APIError(e.message)


# ------------------Chat-----------------------
@app.route('/api/chat/send', methods=['POST'])
def api_chat_sendmsg():
    try:
        uid = session['uid']
        to = request.form['to']
        content = request.form['content']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.chat.send(uid, to, content).json, mimetype='text/json')


@app.route('/api/chat/recv', methods=['GET', 'POST'])
def api_chat_recvmsg():
    uid = session['uid']
    new = request.args['new'] if 'new' in request.args else False
    limit = request.args['limit'] if 'limit' in request.args else 10

    if 'from' in request.args:
        _from = request.args['from']
        return return_json([json.loads(i.json) for i in api.chat.receive(uid, _from, new, limit=int(limit))])
    else:
        return return_json([json.loads(i.json) for i in api.chat.receive_all(uid, new, limit=int(limit))])


@app.route('/api/chat/my', methods=['GET', 'POST'])
def api_get_my_messages():
    later_than = request.args['later_than'] if 'later_than' in request.args else 0
    return return_json([json.loads(i.json) for i in api.chat.get_my_messages(later_than)])


# ----------------Utilities--------------------
@app.route('/api/notifications', methods=['GET', 'POST'])
def api_get_notifications():
    later_than = request.args['later_than'] if 'later_than' in request.args else 0    
    return return_json(api.notify.get_notifications(later_than), default=lambda obj: obj.dict)


@app.route('/api/abuse_report', methods=['POST'])
def api_abuse_report():
    try:
        uid = session['uid']
        content = request.form['content']
        photo = request.form['photo']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.abuse_report.report_abuse(uid, photo, content).json, mimetype='text/json')


# -------------------Admin back-side operations----------------
@app.route('/api/admin/notification/get', methods=['GET', 'POST'])
def api_admin_notifs_get():
    page = request.args['page'] if 'page' in request.args else 1
    notifs, pagecount = api.admin.get_notifications(page)
    return return_json({"notifications": [i.json for i in notifs], "page": {"page_index": page, "has_previous": int(page) > 1, "has_next": int(page) < pagecount}})



@app.route('/api/admin/notification/send', methods=['POST'])
def api_send_notification():
    try:
        content = request.form['content']
        title = request.form['title']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.notify.send_notification(title, content).json, mimetype='text/json')


@app.route('/api/admin/notification/delete', methods=['GET', 'POST'])
def api_delete_notification():
    try:
        n_id = request.args['id']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.notify.delete_notification(n_id))


@app.route('/api/admin/abuse_report/get', methods=['GET', 'POST'])
def api_process_abuse_report():
    page = request.args['page'] if 'page' in request.args else 1
    return return_json(api.admin.get_abuse_reports(page))


@app.route('/api/admin/abuse_report/read', methods=['GET', 'POST'])
def api_mark_report_as_read():
    try:
        r_id = request.args['id']
    except KeyError, e:
        raise APIError(e.message)

    return api.abuse_report.mark_as_read(r_id)


@app.route('/api/admin/send_msg', methods=['POST'])
def api_admin_send_message():
    try:
        users = request.form['users']
        is_global = request.form['is_global']
        content = request.form['content']
        is_mutual = request.form['is_mutual']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.group_message(users, is_global, content, is_mutual))


@app.route('/api/admin/stat', methods=['GET', 'POST'])
def api_admin_get_stat():
    page = request.args['page'] if 'page' in request.args else 1
    return return_json(api.admin.get_stat_info(page))


@app.route('/api/admin/user/get', methods=['GET', 'POST'])
def api_admin_get_users():
    page = request.args['page'] if 'page' in request.args else 1
    phone = request.args['phone'] if 'phone' in request.args else ''
    return return_json(api.admin.get_users(page, phone))


@app.route('/api/admin/user/resetpwd', methods=['GET', 'POST'])
def api_admin_reset_pwd():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.reset_user_pwd(uid))


@app.route('/api/admin/user/delete', methods=['GET', 'POST'])
def api_admin_delete_user():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.delete_user(uid))


@app.route('/api/admin/user/chmod', methods=['GET', 'POST'])
def api_admin_user_chmod():
    try:
        uid = request.args['uid']
        mode = request.args['mode']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.chmod(uid, mode))


@app.route('/api/admin/user/add', methods=['GET', 'POST'])
def api_admin_user_add():
    try:
        phone = request.args['phone']
        password = request.args['password']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.useradd(phone, password))


@app.route('/api/admin/user/school/inprogresses', methods=['GET', 'POST'])
def api_admin_school_inprogress_list():
    page = request.args['page'] if 'page' in request.args else 1
    return return_json(api.admin.get_users_in_progress(page))


@app.route('/api/admin/user/school/pass', methods=['GET', 'POST'])
def api_admin_school_pass():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.pass_user_school(uid, True))


@app.route('/api/admin/user/school/reject', methods=['GET', 'POST'])    
def api_admin_school_reject():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.admin.pass_user_school(uid, False))


# -----------------Common-------------------------
@app.route('/api/common/license', methods=['GET', 'POST'])
def get_license():
    return return_json(api.common.get_license())


@app.route('/api/common/horoscope', methods=['GET', 'POST'])
def get_horoscope():
    return return_json(api.common.get_horoscopes())


@app.route('/api/common/province', methods=['GET', 'POST'])
def get_province():
    return return_json(api.common.get_provinces())


@app.route('/api/common/city', methods=['GET', 'POST'])
def get_city():
    try:
        province = request.args['province'].strip()
        return return_json(api.common.get_cities(province))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/common/school', methods=['GET', 'POST'])
def get_school():
    return return_json(api.common.get_schools())


@app.route('/api/common/major', methods=['GET', 'POST'])
def get_major():
    return return_json(api.common.get_majors())


@app.route('/api/ua/check_uc', methods=['GET','POST'])
def check_if_uc():
    ua = request.headers.get('User-Agent')
    if not ua:
        return jsonify({'code':-1})
    if ua.find('UC') != -1:
        return jsonify({'code':1})
    else:
        return jsonify({'code':-1})

@app.route('/api/ua/check_qq', methods=['GET','POST'])
def check_if_qq():
    ua = request.headers.get('User-Agent')
    if not ua:
        return jsonify({'code':-1})
    if ua.find('QQ') != -1 or ua.find('Sogou') != -1:
        return jsonify({'code':1})
    else:
        return jsonify({'code':-1})

#############################################################
##########  TEST admin API goes here#########################
##########  Remove code below later #########################
TEST_ADMIN_PASSWORD = 'xiaoyuadmin2015'

@app.route('/api/test/manage/users', methods=['POST'])
def test_admin_get_all_users():
    if (request.form['password'] != TEST_ADMIN_PASSWORD):
        return return_json({'error':'Invalid password.'})
    from model import UserMeta
    all_users_raw = UserMeta.query.all()
    all_users = [ json.loads(user.json) for user in all_users_raw]
    return return_json(all_users)

@app.route('/api/test/manage/pass_user', methods=['POST'])
def test_admin_pass_user_school_info():
    if (request.form['password'] != TEST_ADMIN_PASSWORD):
        return return_json({'error':'Invalid password.'})
    return return_json(json.loads(api.user.pass_user_school(int(request.form['uid'])).json))


###########################################################
################ Auto login redirection ###################
###########################################################

@app.route('/api/user/autologin', methods=['GET'])
def user_check_autologin():
    if ('uid' in session and 'phone' in session):
        return redirect('/app.html')
    else:
        return redirect('/index.html')
