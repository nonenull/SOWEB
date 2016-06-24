# -*- coding: utf-8 -*-
from System.model import db
import time

def index(request):
    a = 'fuckyou'
    db.insertMany('bpbjj.users', [{'playerid': 1, 'playerName': a},{'playerid': 2, 'playerName': a},{'playerid': 3, 'playerName': a},{'playerid': 4, 'playerName': a}])
    context = { 'items': ['<AAA>', 'B&B', '"CCC"'] }
    return request.render('index.html', context)
