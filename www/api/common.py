# -*- coding: utf-8 -*-

from model import db
from model import License, Horoscope, Province, City, School, Major
import json


def get_license():
    license = License.query.first()
    content = ''
    if not license:
        content = '用户协议还没有添加'
    else:
        content = license.content
    return {'content': content}


def get_horoscopes():
    horoscopes = Horoscope.query.all()
    return [{item.id : item.name} for item in horoscopes]


def get_provinces():
    provinces = Province.query.all()
    return [{item.id : item.name} for item in provinces]


def get_cities(province):
    cities = City.query.filter_by(province=province).all()
    return [{item.id : item.name} for item in cities]


def get_schools():
    schools = School.query.all()
    return [{item.id : item.name} for item in schools]

def get_majors():
    majors = Major.query.all()
    return [{item.id : item.name} for item in majors]