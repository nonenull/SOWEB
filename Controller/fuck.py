# -*- coding: utf-8 -*-

import time


def index(request):
    context = { 'items': ['<AAA>', 'B&B', '"CCC"'] }
    return request.render('index.html', context)
    # return request.render(file='index.html',data = {'contents':'fuckyou','title':random.uniform(10, 20)})
