# -*- coding: utf-8 -*-

import time
import random

def index(request):
    return request.render(file='index.html',data = {'contents':'fuckyou','title':random.uniform(10, 20)})
