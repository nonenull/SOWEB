# -*- coding: utf-8 -*-
from helper import Helper
import log as logging
import time, select
from Config.config import TIMEOUT


class TimeOut:
    def __init__(self, serverFd, queue):
        self.serverFd = serverFd
        self.timeOutQueue = queue
        self.startGetQueue()

    def startGetQueue(self):
        while 1:
            if not self.timeOutQueue.empty():
                clientFd, acceptTime = self.timeOutQueue.get()
                logging.debug('收到请求 %d %f' % (clientFd, acceptTime))
                try:
                    self.checkTimeOut(clientFd, acceptTime)
                except Exception as message:
                    logging.error('超时判断结束了 %s  %s'%(message,Helper().getTraceStackMsg()))
                    pass

    def checkTimeOut(self, clientFd, acceptTime):
        while 1:
            if time.time() - acceptTime == TIMEOUT:
                logging.debug('%d %f 超时了 %f' % (clientFd, acceptTime, time.time()))
                self.serverFd.modify(clientFd, select.EPOLLET | select.EPOLLERR)
                break
