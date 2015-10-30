# -*- coding: utf-8 -*-

from flask import session
from model import User, Photo, db
from api import APIError
import api.photo, time, os


def upload_photo(imagedata, desc, args):
    uid = session['uid']
    existing_photos = Photo.query.filter_by(user=uid).count()
    if existing_photos >= 50:
        raise APIError('相册已有50张图片，达到上限了')

    photo = Photo()
    photo.user = uid
    photo.url = api.photo.upload_photo(imagedata, args)
    photo.desc = desc
    photo.created_at = time.time()

    db.session.add(photo)
    db.session.commit()
    return photo


def get_all_photos(uid):
    return Photo.query.filter_by(user=uid).order_by(Photo.created_at.desc()).all()


def remove_photo(id):
    photo = Photo.query.filter_by(id=id).first()
    if not photo:
        raise APIError('照片不存在')
    if photo.user != session['uid']:
        raise APIError('不是自己的照片')
    try:
        os.remove(photo.url)
    except Exception:
        pass
    db.session.delete(photo)
    db.session.commit()
    return {"id": id}

