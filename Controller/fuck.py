# -*- coding: utf-8 -*-
# from System.model import db
import time
import requests
from System.mylog import myLogging as logging
def index(r):
    config = {
        # 这里./ 是Upload目录
        'PATH':'./up/fuck',
        'MAX_SIZE' : 10000000,
        'ALLOWED_FILE_SUFFIX':['docx','jpg','png','txt','chm']
    }
    result = r.saveFile('file',config)
    if result == True:
        return '上传成功'
    else:
        return result
    # db.insertMany('bpbjj.users', [{'playerid': 1, 'playerName': a},{'playerid': 2, 'playerName': a},{'playerid': 3, 'playerName': a},{'playerid': 4, 'playerName': a}])
    # context = { 'items': ['<AAA>', 'B&B', '"CCC"'] }
    # return request.render('index.html', context)
