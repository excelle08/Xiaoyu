# -*- coding: utf-8 -*-

from urls import app
from config.config import configs
from api import datetime_filter

def get_mysql_conn_str():
    db_user = configs.db.user
    db_pass = configs.db.password
    db_name = configs.db.database
    db_host = configs.db.host
    db_port = configs.db.port

    return 'mysql+mysqlconnector://' + db_user + ':' + db_pass + '@' + db_host + ':' + str(db_port) + '/' + db_name


def run_app(environ, start_response):
    app.config['SQLALCHEMY_DATABASE_URI'] = get_mysql_conn_str()
    app.config.from_object('config.config')
    app.jinja_env.filters['datetime'] = datetime_filter
    return app(environ, start_response)

if __name__=='__main__':
    run_app(None, None)
