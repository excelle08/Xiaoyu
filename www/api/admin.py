# -*- coding: utf-8 -*-

from api.statistics import get_pv_counts
from model import User, UserMeta, Notification, PageView, Wall
import time, json, datetime


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