# -*- coding:utf-8 -*-
import time
import random

def index(request):
    time.sleep(10)
    return '123123'
    # return request.render(file='index.html',data = {'contents':'fuckyou','title':random.uniform(10, 20)})
