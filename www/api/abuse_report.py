# -*- coding: utf-8 -*-

from model import db
from model import AbuseReport
from api import check_admin
from api import APIError
from api.photo import upload_photo
import time


def report_abuse(msg_from, photo, content):
    areport = AbuseReport()
    areport.msg_from = msg_from
    areport.photo = photo
    areport.content = content
    areport.read = False
    areport.created_at = time.time()

    db.session.add(areport)
    db.session.commit()

    return areport


def get_reports(page, lines=10):
    page = int(page)
    if not check_admin():
        raise APIError('You are not the admin.')

    return AbuseReport.query.filter_by(read=0).order_by(AbuseReport.created_at.desc()).offset(lines*(page-1)).limit(lines).all()


def mark_as_read(id):
    if not check_admin():
        raise APIError('You are not the admin')

    rp = AbuseReport.query.filter_by(id=id).first()
    if not rp:
        raise APIError('此条信息不存在。')
    rp.read = 1

    db.session.commit()
    return rp

