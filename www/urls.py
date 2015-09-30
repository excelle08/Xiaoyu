# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify, session, request
from flask import render_template, make_response
from api import APIError, datetime_filter
from captcha import generate_captcha
from config.config import configs
from model import db
import api.common, api.user, api.tweets, api.message, api.friends
import api.photo, api.album 
import json

app = Flask(__name__)
db.init_app(app)


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello World"


@app.route('/api/user/verify', methods=['POST'])
def api_send_verification_sms():
    try:
        phone = request.form['phone']
        return api.user.send_message(phone)
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/register', methods=['POST'])
def api_user_register():
    try:
        phone = request.form['phone']
        password = request.form['password']
        vcode = request.form['vcode']
        
        user = api.user.user_register(phone, password, vcode)
        return json.dumps({"uid": user.uid, "created_at": user.created_at})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/login', methods=['POST'])
def api_user_login():
    try:
        phone = request.form['phone']
        password = request.form['password']
        remember = request.form['remember']

        user = api.user.user_login(phone, password, remember)
        return json.dumps({"uid": user.uid})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/onlines', methods=['GET', 'POST'])
def api_get_online_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return json.dumps(api.user.get_online_users(offset, limit))


@app.route('/api/user/hot', methods=['GET', 'POST'])
def api_get_hot_users():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return json.dumps(api.user.get_hot_users(offset, limit))


@app.route('/api/user/recent_login', methods=['GET', 'POST'])
def api_get_recent_logins():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    return json.dumps(api.user.get_recent_logins(offset, limit))


@app.route('/api/user', methods=['GET', 'POST'])
def api_get_user():
    try:
        uid = session['uid']
        u = api.user.get_user(uid)
        u.password = ''
        return json.dumps(u)
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/meta', methods=['GET', 'POST'])
def api_get_user_meta():
    uid = request.args['uid'].strip() if "uid" in request.args else session['uid']
    return json.dumps(api.user.get_user_meta(uid))


@app.route('/api/user/ext', methods=['GET', 'POST'])
def api_get_user_ext():
    uid = request.args['uid'].strip() if "uid" in request.args else session['uid']
    return json.dumps(api.user.get_user_extension(uid))


@app.route('/api/user/friends/add', methods=['GET', 'POST'])
def api_add_friend():
    try:
        target = request.args['target'].strip()
        group = request.args['group'].strip() if 'group' in request.args else 0
    except KeyError, e:
        raise APIError(e.message)

    return json.dumps(api.friends.add_friends(target, group))

@app.route('/api/user/friends', methods=['GET', 'POST'])
def api_get_friends():
    return json.dumps(api.friends.get_friends())


@app.route('/api/user/friends/groups', methods=['GET', 'POST'])
def api_get_friends_group():
    return json.dumps(api.friends.get_friend_groups())


@app.route('/api/user/friends/groups/add', methods=['GET', 'POST'])
def api_add_friends_group():
    try:
        title = request.args['title'].strip()
        return json.dumps(api.friends.add_friend_group(title))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/groups/delete', methods=['GET', 'POST'])
def api_delete_friends_group():
    try:
        g_id = request.args['id'].strip()
        return json.dumps(api.friends.delete_friend_group(g_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/groups/modify', methods=['GET', 'POST'])
def api_modify_friend_group():
    try:
        g_id = request.args['id'].strip()
        title = request.args['title'].strip()
        return json.dumps(api.friends.rename_friend_group(g_id, title))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/friends/agree', methods=['GET', 'POST'])
def api_agree_friends_request():
    try:
        req_id = request.args['req_id'].strip()
        group = request.args['group'] if 'group' in request.args else 0
    except KeyError, e:
        raise APIError(e.message)

    return json.dumps(api.friends.agree_friend(req_id, group))


@app.route('/api/user/friends/delete', methods=['GET', 'POST'])
def api_delete_friend():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return json.dumps(api.friends.delete_friend(uid))


@app.route('/api/user/blacklist/add', methods=['GET', 'POST'])
def api_add_to_blacklist():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return json.dumps(api.friends.add_to_blacklist(uid))


@app.route('/api/user/blacklist/delete', methods=['GET', 'POST'])
def api_delete_from_blacklist():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        raise APIError(e.message)

    return json.dumps(api.friends.remove_from_blacklist(uid))


@app.route('/api/tweet/add', methods=['POST'])
def api_add_tweet():
    try:
        content = request.form['content']
        photos = request.form.getlist['photos']
    except KeyError, e:
        raise APIError(e.message)
    visibility = request.form['visibility'] if 'visibility' in request.form else 0
    return json.dumps(api.tweets.write_tweet(content, photos, visibility))


@app.route('/api/tweet/getall', methods=['GET', 'POST'])
def api_get_friends_tweets():
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip if 'later_than' in request.args else 0
    return json.dumps(api.tweets.get_friends_tweets(offset, limit, later_than))


@app.route('/api/tweet/user', methods=['GET', 'POST'])
def api_get_ones_tweets():
    try:
        uid = request.args['uid']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip if 'later_than' in request.args else 0
    return json.dumps(api.tweets.get_users_tweets(uid, offset, limit, later_than))


@app.route('/api/tweet/reply', methods=['POST'])
def api_reply_tweet():
    try:
        target_tweet_id = request.form['id'].strip()
        content = request.form['content'].strip()
        visibility = request.form['visibility'].strip() if 'visibility' in request.form else 0
        return json.dumps(api.tweets.reply(target_tweet_id, content, visibility))
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
    later_than = request.args['later_than'].strip if 'later_than' in request.args else 0
    return json.dumps(api.tweets.get_replies(tweet_id, offset, limit, later_than))


@app.route('/api/tweet/delete', methods=['GET', 'POST'])
def api_tweet_delete():
    try:
        tweet_id = request.args['id'].strip()
        return json.dumps(api.tweets.remove_tweet(tweet_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/tweet/reply/delete', methods=['GET', 'POST'])
def api_reply_delete():
    try:
        reply_id = request.args['id'].strip()
        return json.dumps(api.tweets.remove_reply(reply_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/photo/upload', methods=['POST'])
def api_upload_photo():
    try:
        photo = request.files['photo']
        url = api.photo.upload_photo(photo, request.args)
        return json.dumps({'url': url})
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/album/upload', methods['POST'])
def api_upload_to_album():
    try:
        photo = request.files['photo']
        desc = request.form['desc'] if 'desc' in request.form else ''
        return json.dumps(api.album.upload_photo(photo, desc, request.args))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/album/get', methods=['GET', 'POST'])
def api_get_album_photos():
    uid = request.args['uid'] if 'uid' in request.args else session['uid']
    return json.dumps(api.album.get_all_photos(uid))


@app.route('/api/album/delete', methods=['GET', 'POST'])
def api_remove_photo():
    try:
        photo_id = request.args['id'].strip()
        return json.dumps(api.album.remove_photo(photo_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/add', methods=['POST'])
def api_message_add():
    try:
        target_uid = request.form['uid']
        content = request.form['content']
        visibility = request.form['visibility'] if 'visibility' in request.form else 0
        return json.dumps(api.message.leave_message(target_uid, content, visibility))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/reply/add', methods=['POST'])
def api_message_reply():
    try:
        message_id = request.form['id']
        content = request.form['content'] 
        visibility = request.form['visibility'] if 'visibility' in request.form else 0
        return json.dumps(api.message.reply_message(message_id, content, visibility))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/get', methods=['GET', 'POST'])
def api_message_get():
    uid = request.args['uid'].strip() if 'uid' in request.args else session['uid']
    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip if 'later_than' in request.args else 0
    return json.dumps(api.message.get_messages(uid, offset, limit, later_than))


@app.route('/api/message/reply/get', methods=['GET', 'POST'])
def api_message_reply_get():
    try:
        message_id = request.form['id']
    except KeyError, e:
        raise APIError(e.message)

    offset = request.args['offset'].strip() if 'offset' in request.args else 0
    limit = request.args['limit'].strip() if 'limit' in request.args else 10
    later_than = request.args['later_than'].strip if 'later_than' in request.args else 0
    return json.dumps(api.message.get_replies(message_id, offset, limit, later_than))


@app.route('/api/message/delete', methods=['GET', 'POST'])
def api_message_delete():
    try:
        message_id = request.form['id']
        return json.dumps(api.message.remove_message(message_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/message/reply/delete', methods=['GET', 'POST'])
def api_message_Reply_delete():
    try:
        reply_id = request.form['id']
        return json.dumps(api.message.remove_reply(reply_id))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/common/license', methods=['GET', 'POST'])
def get_license():
    return json.dumps(api.common.get_license())


@app.route('/api/common/horoscope', methods=['GET', 'POST'])
def get_horoscope():
    return json.dumps(api.common.get_horoscopes())


@app.route('/api/common/province', methods=['GET', 'POST'])
def get_province():
    return json.dumps(api.common.get_provinces())


@app.route('/api/common/city', methods=['GET', 'POST'])
def get_city():
    try:
        province = request.args['province'].strip()
        return json.dumps(api.common.get_cities(province))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/common/school', methods=['GET', 'POST'])
def get_school():
    return json.dumps(api.common.get_schools())


def get_mysql_conn_str():
    db_user = configs.db.user
    db_pass = configs.db.password
    db_name = configs.db.database
    db_host = configs.db.host
    db_port = configs.db.port

    return 'mysql+mysqlconnector://' + db_user + ':' + db_pass + '@' + db_host + ':' + str(db_port) + '/' + db_name


if __name__=='__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = get_mysql_conn_str()
    app.config.from_object('config.config')
    app.jinja_env.filters['datetime'] = datetime_filter
    app.run(debug=True)
