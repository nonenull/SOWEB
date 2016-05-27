# -*- coding:utf-8 -*-

from webapi import WebApi
import log as logger
from helper import Helper

Helper = Helper()


class ParseWorker:
    def __init__(self,serverFd,queue):
        self.serverFd = serverFd
        self.parseWorkerQueue = queue
        self.worker()

    def worker(self):
        while 1:
            if not self.parseWorkerQueue.empty():
                try:
                    fd = self.parseWorkerQueue.get()
                    # WebApi(self.serverFd,fd,connParam)
                    print fd
                except Exception as e:
                    logger.error('queue error %s - %s '%(e, Helper.getTraceStackMsg()))
                    pass