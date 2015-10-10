from model import db
from model import Notification, User, UserPermission
from api import APIError, check_admin
import time


def send_notification(content):
    if not check_admin():
        raise APIError('You are not the admin.')

    notification = Notification()
    notification.content = content
    notification.created_at = time.time()
    db.session.add(notification)
    db.session.commit()


def get_notifications(later_than):
    return Notification.query.filter(Notification.created_at >= later_than).order_by(Notification.created_at.desc()).all()


def delete_notification(id):
    if not check_admin():
        raise APIError('You are not the admin.')

    n = Notification.query.filter_by(id=id).first()
    db.session.delete(n)
    db.session.commit()

    return {"id": id}


