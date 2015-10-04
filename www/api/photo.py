# -*- coding: utf-8 -*-

from model import User
from api import APIError
from werkzeug.datastructures import FileStorage
from PIL import Image
import time

accepted_mime = ['image/jpeg', 'image/gif', 'image/png', 'image/tiff']
suffix = ['jpg', 'gif', 'png', 'tiff']

# imagedata should be a FileStorage object
def upload_photo(imgdata, **args):
    if not isinstance(imgdata, FileStorage):
        raise APIError('Field "imgdata" is supposed to be a FileStorage object')
    if not imgdata.mimetype in accepted_mime:
        raise APIError('只能接受JPEG, GIF, PNG或者TIFF格式的图像。')
    if imgdata.content_length > 4*1048576:
        raise APIError('图片大小不能超过4MB')
    name = 'static/upload/%s.%s' % (str(time.time()), suffix[accepted_mime.index(imgdata.mimetype)])
    imgdata.save(name)
    try:
        image = Image.open(name)
        width, height = image.size
        crop_left = args['crop_left'] if 'crop_left' in args else 0
        crop_right = args['crop_right'] if 'crop_right' in args else width
        crop_up = args['crop_up'] if 'crop_up' in args else 0
        crop_down = args['crop_down'] if 'crop_down' in args else height
        image = image.crop((crop_left, crop_up, crop_right, crop_down))

        resize_x = args['resize_x'] if 'resize_x' in args else width
        resize_y = args['resize_y'] if 'resize_y' in args else height
        image = image.resize((resize_x, resize_y), Image.BILINEAR)

        image.save(name)
        return name
    except Exception, e:
        raise APIError(e.message)
