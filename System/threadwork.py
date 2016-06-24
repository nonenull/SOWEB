# -*- coding:utf-8 -*-

import threading, time, queue as Queue
from System.webapi import WebApi
from Config.config import TIMEOUT
from System.mylog import myLogging as logging

class WorkTasksThread(threading.Thread):
    def __init__(self, threadCondition, queue, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.threadCondition = threadCondition
        self.queue = queue
        self.setDaemon(True)

    def processer(self, args):
        try:
            #self.epollFd, fd, connParam
            epollFd, fd, connParam = args
            # 处理请求，并生成response数据
            WebApi(epollFd, fd, connParam)
        except Exception as message:
            logging.error("WorkTasksThread error: %s  %s" % (message))
        finally:
            pass

    def run(self):
        while True:
            try:
                args, kwargs = self.queue.get()
                self.processer(args)
            except Queue.Empty:
                continue

class TimeoutTasksThread(threading.Thread):
    def __init__(self, threadCondition, queue, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.threadCondition = threadCondition
        self.queue = queue
        self.setDaemon(True)

    def processer(self, args):
        try:
            #  {"addr": clientAddr, "connections": clientConn, "acceptTime":acceptTime }
            requestParam = args[0]
            fd = args[1]
            epollFd = args[2]
            startLinkTime = requestParam['acceptTime']

            # 在超时时间内判断是否请求应该成功响应,如果已经响应中断循环
            while time.time() - startLinkTime <= TIMEOUT:
                # 如果 key generateResponseDataTime存在，说明请求已经成功响应，不需要再计算
                if requestParam.has_key('responseTime'):
                    # print('TimeoutTasksThread %d 请求已经成功响应,不执行后续操作' % fd)
                    break
            else:
                # print('TimeoutTasksThread - %d已经超时' % fd)
                # 如果超时之后时间还没变化
                if requestParam['acceptTime'] == startLinkTime:
                    WebApi._epollFd = epollFd
                    WebApi._fd = fd
                    WebApi().fastResponse(504)
                    # 超时之后更改直接注册epoll out 事件，触发Epoll()下__epollOut引发异常断开socket
                    # epollFd.modify(fd, select.EPOLLET | select.EPOLLOUT)
        except Exception as message:
            logging.error('TimeoutTasksThread - %s' % message)

    def run(self):
        while 1:
            try:
                args, kwargs = self.queue.get()
                self.processer(args)
            except Queue.Empty:
                continue
            except:
                logging.error("timeout thread error")


class ThreadPool:
    def __init__(self, numOfThreads=10, role='worker'):
        self.threadCondition = threading.Condition()
        self.role = role
        self.queue = Queue.Queue()
        self.threads = []
        self.__createThreadPool(numOfThreads)

    # 创建线程
    def __createThreadPool(self, numOfThreads):
        #
        # taskDic = {'timeout': TimeoutTasksThread, 'worker': WorkTasksThread}

        for i in range(numOfThreads):
            # thread = taskDic.get(self.role)(self.threadCondition, self.queue)
            thread = WorkTasksThread(self.threadCondition, self.queue)
            self.threads.append(thread)

    def start(self):
        i = 0
        for thread in self.threads:
            thread.start()

    def addJob(self, *args, **kwargs):
        self.queue.put((args, kwargs))
