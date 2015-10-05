from model import db
from model import Wall, User, UserMeta, UserSchool, UserPermission
from api import APIError
import json, time


def user_upwall(uid, title, photo_array):
    if photo_array.__len__() > 8:
        raise APIError('照片不能超过8张')

    user = User.query.filter_by(uid=uid).first()
    if user.permission < UserPermission.Validated:
        raise APIError('你没有权限上墙')

    wall = Wall()
    wall.uid = uid
    wall.photos = json.dumps(photo_array)
    wall.title = title
    wall.upvotes = 0
    wall.created_at = time.time()
    wall.modified_at = time.time()

    db.session.add(wall)
    db.session.commit()

    return set_my_filter(uid, {})


def edit_wall(uid, photo_array, title):
    if photo_array.__len__() > 8:
        raise APIError('照片不能超过8张')
    wall = Wall.query.filter_by(uid=uid).first()

    wall.title = title
    wall.photos = json.dumps(photo_array)
    wall.modified_at = time.time()
    db.session.commit()
    return wall


def set_my_filter(uid, args):
    condition = {
        'school' : args['school'] if 'school' in args else -1,
        'degree' : args['degree'] if 'degree' in args else -1,
        'gender' : args['gender'] if 'gender' in args else -1,
        'age_min' : args['age_min'] if 'age_min' in args else 0,
        'age_max' : args['age_max'] if 'age_max' in args else 9999,
        'height_min' : args['height_min'] if 'height_min' in args else 0,
        'height_min' : args['height_max'] if 'height_max' in args else 9999,
        'hometown_province' : args['hometown_province'] if 'hometown_province' in args else 0,
        'hometown_city' : args['hometown_city'] if 'hometown_city' in args else 0
        'work_province' : args['work_province'] if 'work_province' in args else 0
        'work_city': args['work_city'] if 'work_city' in args else 0
        'horoscope': args['horoscope'] if 'horoscope' in args else 0
    }
    wall = Wall.query.filter_by(uid=uid).first()
    wall.wall_filter = json.dumps(condition)
    wall.modified_at = time.time()

    db.session.commit()
    return wall


def remove_wall(uid):
    wall = Wall.query.filter_by(uid=uid)
    wid = wall.id
    db.session.delete(wall)
    db.session.commit()
    return {"id": wid}


def get_user_wall(uid):
    return Wall.query.filter_by(uid=uid).first()


def upvote_user(uid):
    wall = Wall.query.filter_by(uid=uid).first()
    wall.upvotes += 1

    db.session.commit()
    return wall


def filter_users(uid):
    wall = Wall.query.filter_by(uid=uid).first()

    condition = json.loads(wall.wall_filter)

    # User filter
    users_query = UserMeta.query.filter(UserMeta.age >= condition['age_min'], UserMeta.age <= condition['age_max'], \
        UserMeta.height >= condition['height_min'], UserMeta.height <= condition['height_max'])

    if condition['gender'] != -1:
        users_query = users_query.filter(UserMeta.gender == condition['gender'])

    if condition['hometown_province']:
        users_query = users_query.filter(UserMeta.hometown_province == condition['hometown_province'])

    if condition['hometown_city']:
        users_query = users_query.filter(UserMeta.hometown_city == condition['hometown_city'])

    if condition['work_province']:
        users_query = users_query.filter(UserMeta.workplace_province == condition['work_province'])

    if condition['work_city']:
        users_query = users_query.filter(UserMeta.workplace_city == condition['work_city'])

    if condition['horoscope']:
        users_query = users_query.filter(UserMeta.horoscop == condition['horoscope'])

    users = users_query.all()
    if not users:
        return []
    uids = [ user.uid for user in users ]

    # School filter
    schools_query = UserSchool.query.filter_by(UserSchool.auth_pass == True)

    if condition['school'] != -1:
        schools_query = schools_query.filter_by(UserSchool.school_id == condition['school'])

    if condition['degree'] != -1:
        schools_query = schools_query.filter_by(UserSchool.degree == condition['degree'])

    user_schools = schools_query.all()
    uids2 = [ item.uid for item in user_schools ]

    # Will only display users on the wall.
    users_onwall = [ item.uid for item in Wall.query.all() ]

    result_ids = list(set.intersection(set(uids), set(uids2), set(users_onwall)))

    result = []
    for uid in result_ids:
        result.append(UserMeta.query.filter_by(uid=uid).first())

    return result


def get_guest_wall_items(uid):
    initial = filter_users(uid)

    if initial.__len__() >= 7 and initial.__len__() <= 30 :
        return initial

    if initial.__len__() > 30:
        return initial[:30]

    numbers = 7 - initial.__len__()
    ids = [ item.id for item in Wall.query.ordered_by(Wall.upvotes.desc()).limit(numbers)]
    result = []

    for i in ids:
        result.append(UserMeta.query.filter_by(uid=i).first())
    initial.extend(result)

    return initial

