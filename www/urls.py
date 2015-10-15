# -*- coding: utf-8 -*-

from flask import Flask, Response
from flask import jsonify, session, request
from flask import render_template, make_response
from flask import redirect, url_for
from api import APIError, check_admin
from model import db, UserPermission
import api.common, api.user, api.tweets, api.message, api.friends
import api.photo, api.album, api.wall, api.chat, api.notify, api.abuse_report, api.statistics
import json, re

app = Flask(__name__)
db.init_app(app)

nopriv_allowed = [
    '/static/.*',
    '/login',
    '/reg',
    '/api/common/.*',
    '/api/user/verify',
    '/api/user/login',
    '/api/register',
    '/api/test/.*',
    '/test.*'
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
        return redirect('/login')


@app.before_request
def blockeds_interceptor():
    global blocked_allowed

    auth_flag = False

    if 'uid' in session:
        user = api.user.get_user(session['uid'])
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


@app.after_request
def pageview_recorder(req):
    uid = session['uid'] if 'uid' in session else 0
    path = request.path
    ip = request.remote_addr
    api.statistics.pageview(uid, path, ip)
    return req

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


@app.route('/admin/pub_note', methods=['GET', 'POST'])
def admin_publish_nofitication():
    return render_html('pub_note.html')

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
    return return_json({"vcode": api.user.generate_vcode()})

### end


# ---------------User-related backend API---------------------
@app.route('/api/user/verify', methods=['POST'])
def api_send_verification_sms():
    try:
        phone = request.form['phone']
        return Response(api.user.send_message(phone), mimetype="text/json")
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
    return redirect(url_for('.index'))


@app.route('/api/user/onlines', methods=['GET', 'POST'])
def api_get_online_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_online_users(offset, limit), default=lambda obj: obj.dict)


@app.route('/api/user/hot', methods=['GET', 'POST'])
def api_get_hot_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_hot_users(offset, limit), default=lambda obj: obj.dict)


@app.route('/api/user/recent_login', methods=['GET', 'POST'])
def api_get_recent_logins():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return return_json(api.user.get_recent_logins(offset, limit), default=lambda obj: obj.dict)


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
        status = session['status']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.user.set_user_login_state(uid, status).json, mimetype='text/json')


@app.route('/api/user/meta', methods=['GET', 'POST'])
def api_get_user_meta():
    uid = request.args['uid'].strip() if "uid" in request.args else session['uid']
    return Response(api.user.get_user_meta(uid).json, mimetype='text/json')


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
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return Response(api.user.get_user_school(uid).json, mimetype='text/json')


@app.route('/api/user/password/edit', methods=['POST'])
def api_edit_password():
    uid = session['uid']
    original = request.form['original']
    new = request.form['new']
    vcode = request.form['vcode']
    api.user.set_user_password(uid, original, new, vcode)
    return redirect(url_for('.index'))


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
    return return_json(api.friends.get_blacklist())


@app.route('/api/user/blacklist/delete', methods=['GET', 'POST'])
def api_delete_from_blacklist():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return return_json(api.friends.remove_from_blacklist(uid))


#    -------------W A L L---------------
@app.route('/api/wall/go', methods=['POST'])
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
    new_photos = request.form.getlist('photos')
    new_title = request.form['title']
    return Response(api.wall.set_my_photos(uid, new_photos, title).json, mimetype='text/json')


@app.route('/api/wall/upvote', methods=['GET', 'POST'])
def api_upvote_user():
    try:
        uid = session['uid']
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
    return return_json(api.tweets.get_friends_tweets(offset, limit, later_than), default=lambda obj: obj.dict)


@app.route('/api/tweet/user', methods=['GET', 'POST'])
def api_get_ones_tweets():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.tweets.get_users_tweets(uid, offset, limit, later_than), default=lambda obj:obj.dict)


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
        url = api.photo.upload_photo(photo, request.args)
        return return_json({'url': url})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/album/upload', methods=['POST'])
def api_upload_to_album():
    try:
        photo = request.files['photo']
        desc = request.form['desc'] if 'desc' in request.form else ''
        return Response(api.album.upload_photo(photo, desc, request.args).json, mimetype='text/json')
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
    return return_json(api.message.get_messages(uid, offset, limit, later_than), default=lambda obj: obj.dict)


@app.route('/api/message/reply/get', methods=['GET', 'POST'])
def api_message_reply_get():
    try:
        message_id = request.args['id']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip() if 'later_than' in request.args else 0
    return return_json(api.message.get_replies(message_id, offset, limit, later_than), default=lambda obj: obj.dict)


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
        reply_id = request.form['id']
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

    if 'from' in request.args:
        _from = request.args['from']
        return return_json([i.json for i in api.chat.receive(uid, _from)])
    else:
        return return_json([i.json for i in api.chat.receive_all(uid)])


# ----------------Utilities--------------------
@app.route('/api/notifications', methods=['GET', 'POST'])
def api_get_notifications():
    later_than = request.args['later_than'] if 'later_than' in request.args else 0    
    return return_json(api.notify.get_notifications(later_than), default=lambda obj: obj.dict)


@app.route('/api/abuse_report', methods=['POST'])
def api_abuse_report():
    try:
        uid = session['uid']
        target = request.form['target']
        content = request.form['content']
    except KeyError, e:
        raise APIError(e.message)

    return Response(api.abuse_report.report_abuse(uid, target, content).json, mimetype='text/json')


# -------------------Admin back-side operations----------------
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
    filter_read = request.args['filter_read'] if 'filter_read' in request.args else True
    return return_json(api.abuse_report.get_reports(filter_read), default=lambda obj: obj.dict)


@app.route('/api/admin/abuse_report/read', methods=['GET', 'POST'])
def api_mark_report_as_read():
    try:
        r_id = request.args['id']
    except KeyError, e:
        raise APIError(e.message)

    return api.abuse_report.mark_as_read(r_id)


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
