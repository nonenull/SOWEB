# -*- coding:utf-8 -*-

import errno, time, os, compileall, select, threading, socket
import Queue
from Config import config
from System import log as logging
from System.helper import Helper
from threadwork import ThreadPool
from webapi import WebApi

''' 执行Helper类中的初始准备工作 '''
Helper = Helper()
Helper.addSysPath()


class Epoll:
    def __init__(self, serverFd):
        self.serverFd = serverFd
        self.serverFdFileNo = serverFd.fileno()
        self._connParams = {}
        self.childProcess = {}
        self.pid = os.getpid()

        # 限制连接数
        self.acceptQueue = Queue.Queue(config.WORKER_CONNECTIONS)
        self.recvQueue = Queue.Queue()
        self.sendQueue = Queue.Queue()

        self.workThread = ThreadPool(config.THREADS_NUM)
        self.workThread.start()

        # 创建epoll,注册事件
        self.createEpoll()

        threading.Thread(target=self.acceptHandle, args=(self.epollFd, self.acceptQueue)).start()
        threading.Thread(target=self.recvHandle, args=(self.epollFd, self.recvQueue, self.workThread)).start()
        threading.Thread(target=self.sendHandle, args=(self.epollFd, self.sendQueue)).start()

        # 开始处理事件
        self.epollEventHandle()

    def acceptHandle(self, epollFd, acceptQueue):
        while 1:
            if acceptQueue.empty():
                continue

            clientConn, clientAddr = acceptQueue.get_nowait()
            try:
                # 设置新的socket连接为非阻塞
                clientConn.setblocking(0)

                clientConn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                clientFd = clientConn.fileno()
                logging.debug('accept到新的client连接 -%d %s' % (clientFd, clientAddr))

                acceptTime = time.time()
                self._connParams[clientFd] = {"addr": clientAddr, "connections": clientConn, "acceptTime": acceptTime}

                # 向 epoll 句柄中注册 连接 socket 的 可读 事件
                epollFd.register(clientFd, select.EPOLLET | select.EPOLLIN)
            except socket.error:
                # 因为是多个进程竞争,所以其它进程会收到socket错误,需要忽略掉
                pass

    def recvHandle(self, epollFd, recvQueue, workThread):
        while 1:
            if recvQueue.empty():
                continue

            fd = recvQueue.get_nowait()
            logging.debug('%d - 开始接收数据' % fd)
            # 获取抓到的socket连接的信息
            connParam = self._connParams.get(fd)
            # logging.debug(connParam)
            # 开始接收数据
            totalDatas = ''
            while 1:
                try:
                    data = connParam['connections'].recv(config.BUFFER_SIZE)
                    totalDatas += data
                except socket.error as message:
                    # 在 非阻塞 socket 上进行 recv 需要处理 读穿 的情况这里
                    if message.errno == errno.EAGAIN:
                        connParam['requestData'] = totalDatas
                        connParam['recvTime'] = time.time()
                        # logging.debug('=====================', totalDatas)
                        # self.workerThread.apply_async(WebApi,args=(self.epollFd, fd, connParam))
                        WebApi(epollFd, fd, connParam)
                        # gevent.spawn(WebApi,self.epollFd, fd, connParam)
                        # logging.debug('resc DATA %s'%(totalDatas))
                        # workThread.addJob(epollFd, fd, connParam)

                    else:
                        logging.error('resv错误 %d %s' % (fd, message))
                        self.clearFd(fd)
                    break
                finally:
                    pass

    def sendHandle(self, epollFd, sendQueue):
        while 1:
            if sendQueue.empty():
                continue

            fd = sendQueue.get_nowait()
            logging.debug('%d - %d - %d - 开始send数据 -----------'%(fd,self.pid,sendQueue.qsize()))
            # print self._connParams,self._connParams.get(fd)
            # 获取连接数据
            responseParam = self._connParams.get(fd)

            # 获取响应数据
            responseData = responseParam.get('responseData')

            if not responseData:
                logging.error('responseData为空  下面将执行clearFd()' % fd)
                self.clearFd(fd)

            currentClientConn = responseParam['connections']

            try:
                # sendDataToClient()
                currentClientConn.sendall(responseData)
                # while sendLen <= responseDataLen:
                #     sendLen = currentClientConn.sendto(responseData,addr)
            except socket.error as message:
                logging.error('进程ID:%d - 文件描述符:%d - __epollOut()发送响应数据错误,原因:%s  下面将执行pass' % (self.pid, fd, message))
            else:
                responseParam['responseTime'] = time.time()
                self.clearFd(fd)
                logging.debug('%d - 发送完毕\n'%fd)
            # # 如果没有指定keepalived,执行clearFd()断开连接，否则不断开,保持住连接以继续接受数据
            #     # if not responseParam.get('keepalive', None):
            #
            #     # else:
            #     #     self._connParams[fd] = {"addr": responseParam['addr'],
            #     #                             "connections": currentClientConn}
            #     #     # 更新 epoll 句柄中连接 fd 注册事件为 可读
            #     #     self.epollFd.modify(fd, select.EPOLLET | select.EPOLLIN)
            #     #     logging.info('进程ID:%d - 文件描述符:%d -数据成功响应 %s       %s    %d  ' % (
            #     #         self.pid, fd, str(responseParam['addr']), responseParam['responseData'][:15],
            #     #         responseParam['responseTextLen']))
            finally:
                pass

    def createEpoll(self):
        # 开始EPOLL处理
        try:
            # 创建epoll并且注册事件
            self.epollFd = epollFd = select.epoll(config.WORKER_CONNECTIONS)
            epollFd.register(self.serverFdFileNo, select.EPOLLIN)
        except select.error as message:
            logging.error('createEpoll错误 %s' % message)

    def epollEventHandle(self):
        ''' 事件分拣 '''

        def eventSorting(events):
            fileNo, event = events
            eventsDict.get(event, self.clearFd)(fileNo)

        ''' 使用map '''
        eventsDict = {select.EPOLLIN: self.__epollIn, select.EPOLLOUT: self.__epollOut}

        try:
            while 1:
                events = self.epollFd.poll(timeout=1)
                logging.debug('发生事件',events)
                map(eventSorting, events)
                # 死循环 实时获取epoll中的事件
                # for fileNo, event in events:
                #     eventsDict.get(event, self.clearFd)(fileNo)
        except KeyError as message:
            # 变量dict以外的事件不处理
            logging.error(
                '进程ID:%d - epollEventHandle() - 事件超出范围 - 错误代码: %s ' % (self.pid, message))
        except Exception as message:
            logging.error(
                '进程ID:%d - epollEventHandle() - 错误代码: %s ' % (self.pid, message))
        finally:
            pass

    '''
     处理与客户端的连接
    '''

    def __epollIn(self, fd):
        '''
            如果fd等于serverFdFileNo,说明是服务端监听socket有事件发生
        '''
        if fd == self.serverFdFileNo:
            self.acceptQueue.put_nowait(self.serverFd.accept())
        else:
            # 根据config配置决定是否更新pyc文件
            if config.AUTO_RELOAD:
                compileall.compile_dir(r'./', quiet=1)

            self.recvQueue.put_nowait(fd)
            logging.debug('塞入recv队列 - %d' % fd)

    # 发送响应数据
    def __epollOut(self, fd):
        self.sendQueue.put_nowait(fd)
        print('==========')

    # 清空fd相关连接和变量
    def clearFd(self, fd):
        try:
            self.epollFd.unregister(fd)
            param = self._connParams[fd]
            param.get('connections').shutdown(socket.SHUT_RDWR)
            param.get('connections').close()
            del self._connParams[fd]
        except socket.error as message:
            logging.error('clearFd错误 %s' % (message))
            pass