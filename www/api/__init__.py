# -*- coding: utf-8 -*-

import json
import time
import hashlib
from datetime import datetime
from model import User, UserPermission
from flask import session


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=200, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.status_code
        rv['data'] = ''
        rv['message'] = self.message
        return rv


def dump_class(cls):
    return json.dumps(cls, default=lambda obj: obj.__dict__)


def datetime_filter(t):
    if not t:
        t = 0;
    delta = int(time.time() - t)
    if delta < 60:
        return u'1 minute ago'
    if delta < 3600:
        return u'%s minutes ago' % (delta // 60)
    if delta < 86400:
        return u'%s hours ago' % (delta // 3600)
    if delta < 604800:
        return u'%s days ago' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s/%s/%s' % (dt.year, dt.month, dt.day)


def check_admin():
    uid = session['uid']
    u = User.query.filter_by(uid=uid).first()
    return u.permission == UserPermission.Admin