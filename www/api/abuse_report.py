# -*- coding: utf-8 -*-

from model import db
from model import AbuseReport
from api import check_admin
from api import APIError
from api.photo import upload_photo
import time


def report_abuse(_from, photo, content):
    areport = AbuseReport()
    areport._from = _from
    areport.photo = upload_photo(photo)
    areport.content = content
    areport.read = False
    areport.created_at = time.time()

    db.session.add(areport)
    db.session.commit()

    return areport


def get_reports(filter_read = True):
    if not check_admin():
        raise APIError('You are not the admin.')

    return AbuseReport.query.filter_by(read=(not filter_read)).order_by(AbuseReport.created_at.desc()).all()


def mark_as_read(id):
    if not check_admin():
        raise APIError('You are not the admin')

    rp = AbuseReport.query.filter_by(id=id).first()
    if not rp:
        raise APIError('此条信息不存在。')
    rp.read = True

    db.session.commit()
    return rp

