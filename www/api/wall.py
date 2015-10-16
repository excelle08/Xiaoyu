# -*- coding: utf-8 -*-

from model import db
from model import Wall, User, UserMeta, UserSchool, UserPermission, WallUpvote
from api import APIError
import json, time


def user_upwall():

    uid = session['uid']

    user = User.query.filter_by(uid=uid).first()
    if user.permission < UserPermission.Validated:
        raise APIError('你没有权限上墙')

    wall = Wall.query.filter_by(uid=uid).first()
    wall.published = True
    wall.created_at = time.time()

    db.session.commit()

    return set_my_filter(uid, {})


def edit_wall(uid, cover, title, content):
    if photo_array.__len__() > 8:
        raise APIError('照片不能超过8张')
    wall = Wall.query.filter_by(uid=uid).first()

    wall.cover = cover
    wall.title = title
    wall.content = content
    wall.modified_at = time.time()
    db.session.commit()
    return wall


def set_my_filter(uid, args):
    condition = {
        'on': args['on'] if 'on' in args else False,
        'school' : args['school'] if 'school' in args else -1,
        'degree' : args['degree'] if 'degree' in args else -1,
        'major' : args['major'] if 'major' in args else -1,
        'gender' : args['gender'] if 'gender' in args else -1,
        'age_min' : args['age_min'] if 'age_min' in args else 0,
        'age_max' : args['age_max'] if 'age_max' in args else 9999,
        'height_min' : args['height_min'] if 'height_min' in args else 0,
        'height_max' : args['height_max'] if 'height_max' in args else 9999,
        'hometown_province' : args['hometown_province'] if 'hometown_province' in args else 0,
        'hometown_city' : args['hometown_city'] if 'hometown_city' in args else 0,
        'work_province' : args['work_province'] if 'work_province' in args else 0,
        'work_city': args['work_city'] if 'work_city' in args else 0,
        'horoscope': args['horoscope'] if 'horoscope' in args else 0,
        'last_active': args['last_active'] if 'last_active' in args else 0
    }
    wall = Wall.query.filter_by(uid=uid).first()
    wall.wall_filter = json.dumps(condition)
    wall.modified_at = time.time()

    db.session.commit()
    return wall

filter_default = {
    'on': False,
    'school' : -1,
    'degree' : -1,
    'gender' : -1,
    'age_min' : 0,
    'age_max' : 9999,
    'height_min' : 0,
    'height_max' : 9999,
    'hometown_province' : 0,
    'hometown_city' : 0,
    'work_province' : 0,
    'work_city': 0,
    'horoscope': 0,
    'last_active': 0
}


def cancel_wall(uid):
    wall = Wall.query.filter_by(uid=uid)
    wid = wall.uid
    wall.published = False
    db.session.commit()
    return {"id": wid}


def get_user_wall(uid):
    return Wall.query.filter_by(uid=uid).first()


def upvote_user(uid):
    wall = Wall.query.filter_by(uid=uid).first()
    wall.upvotes += 1

    upvote = WallUpvote()
    upvote.uid = uid
    upvote.target = wall.uid
    upvote.new = True
    upvote.time = time.time()

    db.session.add(upvote)
    db.session.commit()
    return upvote


def get_new_upvotes(uid):
    upvotes = WallUpvote.query.filter_by(new=True).order_by(WallUpvote.time.desc()).all()
    for i in upvotes:
        i.new = False

    db.session.commit()
    return upvotes


def get_all_my_upvotes(uid):
    return WallUpvote.query.order_by(WallUpvote.time.desc()).all()


def filter_users(uid):
    wall = Wall.query.filter_by(uid=uid).first()

    condition = json.loads(wall.wall_filter.replace('\\', ''))

    if('on' in condition and condition['on']):

        # User filter
        users_query = UserMeta.query.filter(UserMeta.age >= (condition['age_min'] if 'age_min' in condition else 0), 
            UserMeta.age <= (condition['age_max'] if 'age_max' in condition else 9999),
            UserMeta.height >= (condition['height_min'] if 'height_min' in condition else 0), 
            UserMeta.height <= (condition['height_max'] if 'height_max' in condition else 9999))
    
        if 'gender' in condition and condition['gender'] != -1:
            users_query = users_query.filter(UserMeta.gender == condition['gender'])
    
        if 'hometown_province' in condition and condition['hometown_province']: 
            users_query = users_query.filter(UserMeta.hometown_province == condition['hometown_province'])
    
        if condition['hometown_city']:
            users_query = users_query.filter(UserMeta.hometown_city == condition['hometown_city'])
    
        if condition['work_province']:
            users_query = users_query.filter(UserMeta.workplace_province == condition['work_province'])
    
        if condition['work_city']:
            users_query = users_query.filter(UserMeta.workplace_city == condition['work_city'])
    
        if condition['horoscope']:
            users_query = users_query.filter(UserMeta.horoscope == condition['horoscope'])
    
        users = users_query.all()
        if not users:
            return []
        uids = [ user.uid for user in users ]
    
        user2 = User.query.filter(User.last_login >= 0)
    
        if condition['last_active']:
            user2 = user2.filter(User.last_login >= condition['last_active']).all()
    
        uid1 = [ user.uid for user in user2 ]
    
        # School filter
        schools_query = UserSchool.query.filter(UserSchool.auth_pass == True)
    
        if condition['school'] != -1:
            schools_query = schools_query.filter(UserSchool.school_id == condition['school'])
    
        if condition['degree'] != -1:
            schools_query = schools_query.filter(UserSchool.degree == condition['degree'])
    
        if condition['major'] != -1:
            schools_query = schools_query.filter(UserSchool.major == condition['major'])
    
        user_schools = schools_query.all()
        uids2 = [ item.uid for item in user_schools ]
    
        # Will only display users on the wall.
        users_onwall = [ item.uid for item in Wall.query.all() ]
    
        result_ids = list(set.intersection(set(uids), set(uid1), set(uids2), set(users_onwall)))
    
        result = []
        for uid in result_ids:
            result.append(UserMeta.query.filter_by(uid=uid).first())
    
        return result
    else:
        return UserMeta.query.all()
    

def get_guest_wall_items(uid):
    initial = filter_users(uid)

    if initial.__len__() >= 7 and initial.__len__() <= 30 :
        return initial

    if initial.__len__() > 30:
        return initial[:30]

    numbers = 7 - initial.__len__()
    ids = [ item.id for item in Wall.query.filter_by(published=True).order_by(Wall.created_at.desc()).limit(numbers)]
    result = []

    for i in ids:
        result.append(UserMeta.query.filter_by(uid=i).first())
    initial.extend(result)

    return initial

