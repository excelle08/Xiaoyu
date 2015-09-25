# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify, session, request
from flask import render_template, make_response
from api import APIError, datetime_filter
from captcha import generate_captcha
from config.config import configs
from model import db
import api.common
import json

app = Flask(__name__)
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello World"


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
