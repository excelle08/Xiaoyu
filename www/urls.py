# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify, session, request
from flask import render_template, make_response
from api import APIError, datetime_filter
from captcha import generate_captcha
from config.config import configs
from model import db
import api.common, api.user, api.tweets
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
    try:
        offset = request.args['offset'].strip()
        limit = request.args['limit'].strip()
        if limit == 0:
            limit = 10;
        return json.dumps(api.user.get_online_users(offset, limit))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/hot', methods=['GET', 'POST'])
def api_get_hot_users():
    try:
        offset = request.args['offset'].strip()
        limit = request.args['limit'].strip()
        if limit == 0:
            limit = 10;
        return json.dumps(api.user.get_hot_users(offset, limit))
    except KeyError, e:
        raise APIError(e.message)


@app.route('/api/user/recent_login', methods=['GET', 'POST'])
def api_get_recent_logins():
    try:
        offset = request.args['offset'].strip()
        limit = request.args['limit'].strip()
        if limit == 0:
            limit = 10;
        return json.dumps(api.user.get_recent_logins(offset, limit))
    except KeyError, e:
        raise APIError(e.message)


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
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        uid = session['uid']
    return json.dumps(api.user.get_user_meta(uid))


@app.route('/api/user/ext', methods=['GET', 'POST'])
def api_get_user_ext():
    try:
        uid = request.args['uid'].strip()
    except KeyError, e:
        uid = session['uid']
    return json.dumps(api.user.get_user_extension(uid))


@app.route('/api/tweet/add', methods=['POST'])
def api_add_tweet():
    try:
        content = request.form['content']
        photos = request.form.getlist['photos']
    except KeyError, e:
        raise APIError(e.message)
    try:
        visibility = request.form['visibility']
    except KeyError:
        visibility = 0
    return json.dumps(api.tweets.write_tweet(content, photos, visibility))


@app.route('/api/tweet/reply', methods=['POST'])
def api_reply_post():
    try:
        content = request.form['content']
        target = request.form['target']
    except KeyError, e:
        raise APIError(e.message)
    try:
        visibility = request.form['visibility']
    except KeyError:
        visibility = 0
    return json.dumps(api.tweets.reply(target, content, visibility))


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
