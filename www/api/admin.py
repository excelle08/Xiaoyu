# -*- coding: utf-8 -*-

from api.statistics import get_pv_counts
from api import APIError
from model import User, UserMeta, Notification, PageView, Wall, db, UserSchool, School, Major
import api.user, api.abuse_report, api.message
import time, json, datetime, hashlib


def get_notifications(page, lines=10):
    notifs = Notification.query.order_by(Notification.created_at.desc()).all()
    return notifs[lines*(int(page)-1):lines*int(page)], notifs.__len__() / lines + 1


def get_stat_info(page, lines=10):
    today_pv = PageView.query.filter(PageView.time > time.time() - 86400).count()
    week_pv = PageView.query.filter(PageView.time > time.time() - 86400 * 7).count()
    month_pv = PageView.query.filter(PageView.time > time.time() - 86400 * 30).count()
    total_pv = PageView.query.count()
    onlines = User.query.filter(User.online != 0).count()
    users_with_filter = 0
    walls = Wall.query.all()
    for item in walls:
        user_filter = item.wall_filter
        user_filter = json.loads(user_filter)
        if user_filter['on']:
            users_with_filter += 1

    pv_details = PageView.query.order_by(PageView.time.desc()).limit(300).all()

    pvs = []

    for i in pv_details:
        pv = {}
        if i.user == 0:
            pv["user"] = "<Visitor>"
        else:
            u = User.query.filter_by(uid=i.user).first()
            if u:
                pv["user"] = u.phone
            else:
                pv["user"] = "<Unknown>"
        pv["id"] = i.id
        pv["path"] = i.path
        pv["ip_addr"] = i.ip_addr
        i.time = i.time if isinstance(i.time, float) else 0.0
        pv["time"] = datetime.datetime.fromtimestamp(i.time).strftime('%Y-%m-%d %H:%M:%S')
        pvs.append(pv)

    page_count = 300 / lines

    return {
        "numbers": {
            "today_pv": today_pv,
            "week_pv": week_pv,
            "month_pv": month_pv,
            "total_pv": total_pv,
            "onlines": onlines,
            "users_with_filter": users_with_filter
        },
        "pvs": pvs[lines*(int(page)-1):lines*int(page)],
        "page": {
            "page_index": page,
            "page_count": page_count,
            "has_previous": int(page) > 1,
            "has_next": int(page) < page_count
        }
    }


permissionStr = [ "封禁", "未认证", "认证中", "已通过", "管理员" ]

def get_users(page, phone, lines=10):
    u_query = User.query

    if phone:
        u_query = u_query.filter_by(phone=phone)

    us = u_query.offset(lines*(int(page)-1)).limit(lines).all()
    page_count = us.__len__() / lines + 1
    users = []
    metas = []

    for item in us:
        meta = UserMeta.query.filter_by(uid=item.uid).first()
        user = {
            "uid": item.uid,
            "phone": item.phone,
            "nickname": meta.nickname,
            "permission": permissionStr[item.permission+1],
            "created_at": datetime.datetime.fromtimestamp(item.created_at).strftime('%Y-%m-%d %H:%M:%S'),
            "last_login": datetime.datetime.fromtimestamp(item.last_login).strftime('%Y-%m-%d %H:%M:%S')
        }

        users.append(user)

    return {
        "users": users,
        "metas": metas,
        "page": {
            "page_index": page,
            "has_previous": int(page) > 1,
            "has_next": int(page) < page_count,
            "page_count": page_count
        }
    }


def reset_user_pwd(uid):
    # Will reset pwd to 12345678
    u = User.query.filter_by(uid=uid).first()
    if not u:
        raise APIError('用户不存在')

    u.password = hashlib.md5('12345678').hexdigest()
    db.session.commit()
    return {"STATE": 1}


def delete_user(uid):
    u = User.query.filter_by(uid=uid).first()
    if not u:
        raise APIError('用户不存在')

    db.session.delete(u)
    db.session.commit()

    return {"STATE": 1}


def chmod(uid, mode):
    mode = int(mode)
    if mode < -1 or mode > 3:
        raise APIError('无效的权限值')

    u = User.query.filter_by(uid=uid).first()
    if not u:
        raise APIError('用户不存在。')

    u.permission = mode
    db.session.commit()

    return {"STATE": 1}


def useradd(phone, pwd):
    vcode = api.user.generate_vcode()
    u = api.user.user_register(phone, pwd, vcode, False)
    return {
        "uid": u.uid,
        "phone": u.phone,
        "permission": permissionStr[u.permission + 1],
        "created_at": datetime.datetime.fromtimestamp(u.created_at).strftime('%Y-%m-%d %H:%M:%S'),
        "last_login": datetime.datetime.fromtimestamp(u.last_login).strftime('%Y-%m-%d %H:%M:%S')
    }

degreeStr = ['未知', '本科', '硕士', '博士']

def get_users_in_progress(page, lines=10):
    page = int(page)
    users = User.query.filter(User.permission == 1).offset(lines*(page-1)).limit(lines).all()
    u = []
    for item in users:
        school = UserSchool.query.filter(UserSchool.uid == item.uid).first()
        meta = UserMeta.query.filter(UserMeta.uid == item.uid).first()
        u.append({
            "uid": item.uid,
            "phone": item.phone,
            "nickname": meta.nickname,
            "school": School.query.filter_by(id=school.school_id).first().name if school.school_id else '<N/A>',
            "major": Major.query.filter_by(id=school.major).first().name if school.major else '<N/A>',
            "degree": degreeStr[school.degree] if school.degree else '未知',
            "photo": school.auth_photo
        })

    page_count = users.__len__() / lines + 1

    return {
        "users": u,
        "page": {
            "page_index": page,
            "page_count": page_count,
            "has_previous": page > 1,
            "has_next": page < page_count
        }
    }


def pass_user_school(uid, pass_or_reject):
    if pass_or_reject:
        s = api.user.pass_user_school(uid)
        return {"STATE": 1}
    else:
        user = User.query.filter_by(uid=uid).first()
        if not user:
            raise APIError('用户不存在！')
        user.permission = 0
        db.session.commit()
        return {"STATE": 0}


def get_abuse_reports(page, lines=10):
    reports = api.abuse_report.get_reports(page, lines)
    res = []

    for item in reports:
        from_user = User.query.filter_by(uid=item.msg_from).first()
        from_meta = UserMeta.query.filter_by(uid=item.msg_from).first()
        contents = json.loads(item.content)
        target_id = contents["target_uid"]
        target_user = User.query.filter_by(uid=target_id).first()
        target_meta = UserMeta.query.filter_by(uid=target_id).first()
        res.append({
            "id": item.id,
            "from": {
                "uid": item.msg_from,
                "phone": from_user.phone,
                "nickname": from_meta.nickname
            },
            "photo": item.photo,
            "content": contents["content"],
            "target": {
                "uid": target_id,
                "phone": target_user.phone,
                "nickname": target_meta.nickname
            },
            "read": item.read,
            "created_at": datetime.datetime.fromtimestamp(item.created_at).strftime('%Y-%m-%d %H:%M:%S')
        })

    page_count = res.__len__() / lines + 1

    return {
        "reports": res,
        "page": {
            "page_index": page,
            "page_count": page_count,
            "has_previous": page > 1,
            "has_next": page < page_count
        }
    }


def group_message(user_group, is_global, content, mutual_only):
    uids = []
    is_global = True if is_global.lower() == 'true' else False
    mutual_only = True if mutual_only.lower() == 'true' else False
    success_count = 0
    if is_global:
        users = User.query.all()
        uids = [item.uid for item in users]
    else:
        phones = user_group.split(',')
        for num in phones:
            u = User.query.filter_by(phone=num).first()
            if not u:
                continue
            uids.append(u.uid)
    
    for i in uids:
        api.message.leave_message(i, content, 2 if mutual_only else 0)
        success_count += 1

    return {"OK": success_count}
