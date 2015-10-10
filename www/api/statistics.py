from model import PageView, db
import time


def get_pageviews(later_than):
    return PageView.query.filter(PageView.time >= PageView.later_than).all()


def get_pv_counts(later_than):
    return {"pv": PageView.query.filter(PageView.time >= PageView.later_than).count()}


def pageview(uid, ip, path):
    p = PageView()
    p.user = uid
    p.ip_addr = ip
    p.path = path

    db.session.add(p)
    db.session.commit()