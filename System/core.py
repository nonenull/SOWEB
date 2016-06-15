# -*- coding:utf-8 -*-

import time, os, socket, select
from Config import config
from System import log as logging
from multiprocessing.dummy import Pool as ThreadPool
from System.webapi import WebApi


class Epoll:
    def __init__(self, serverFd):
        self.serverFd = serverFd
        self.serverFdFileNo = serverFd.fileno()
        self._connParams = {}
        self.childProcess = {}
        self.pid = os.getpid()
        self.workerPool = ThreadPool(config.THREADS_NUM)

        # 初始化线程
        # self.workerThread = workerThreadPool(config.THREADS_NUM)
        # self.workerThread.start()

        # 创建epoll,注册事件
        self.createEpoll()

        # 开始处理事件
        self.epollEventHandle()

    '''
        创建EPOLL
    '''

    def createEpoll(self):
        # 开始EPOLL处理
        try:
            # 创建epoll并且注册事件
            self.epollFd = select.epoll()
            self.epollFd.register(self.serverFdFileNo, select.EPOLLIN)
        except select.error as message:
            logging.error('createEpoll错误 %s' % message)

    '''
        使用map来处理时间的分发
    '''

    def epollEventHandle(self):

        eventsDict = {select.EPOLLIN: self.__epollIn, select.EPOLLOUT: self.__epollOut}

        try:
            while 1:
                events = self.epollFd.poll()
                logging.debug('发生事件', events)
                # 死循环 实时获取epoll中的事件
                for fileNo, event in events:
                    eventsDict.get(event, self.clearFd)(fileNo)

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
        # 如果fd等于serverFdFileNo,说明是服务端监听socket有事件发生
        if fd == self.serverFdFileNo:
            clientConn, clientAddr = self.serverFd.accept()
            try:
                # 设置新的socket连接为非阻塞
                clientConn.setblocking(0)
                clientConn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # 获取新连接的文件描述符
                clientFd = clientConn.fileno()
                logging.debug('accept到新的client连接 -%d %s' % (clientFd, clientAddr))
                acceptTime = time.time()
                self._connParams[clientFd] = {"addr": clientAddr, "connections": clientConn, "acceptTime": acceptTime}
                # 向 epoll 句柄中注册 连接 socket 的 可读 事件
                self.epollFd.register(clientFd, select.EPOLLET | select.EPOLLIN)
            except socket.error:
                # 因为是多个进程竞争,所以其它进程会收到socket错误,需要忽略掉
                pass
        else:
            logging.debug('%d - 开始接收数据' % fd)
            # 获取抓到的socket连接的信息
            connParam = self._connParams.get(fd)

            # 开始接收数据
            totalDatas = []
            try:
                while 1:
                    logging.debug('epollIn - 开始recv')
                    data = connParam['connections'].recv(config.RCV_BUFFER_SIZE)
                    if not data: break
                    totalDatas.append(data)
            except socket.error:
                pass

            connParam['requestData'] = ''.join(data.decode('utf-8') for data in totalDatas)
            if '\r\n\r\n' not in connParam['requestData']:
                self.clearFd(fd)
            connParam['recvTime'] = time.time()
            self.workerPool.apply_async(WebApi, args=(self.epollFd, fd, connParam))

    '''
        发送响应数据
    '''

    def __epollOut(self, fd):
        logging.debug('%d - %d -  开始send数据 -----------' % (fd, self.pid))
        # print self._connParams,self._connParams.get(fd)
        # 获取连接数据
        responseParam = self._connParams.get(fd)

        # 获取响应数据
        responseData = responseParam.get('responseData')
        logging.debug('=====', responseData)
        if not responseData:
            logging.error('responseData为空  %d将执行clearFd() ' % fd)
            self.clearFd(fd)
            return

        currentClientConn = responseParam['connections']
        try:
            # sendDataToClient()
            currentClientConn.sendall(responseData.encode('utf-8'))
            # while sendLen <= responseDataLen:
            #     sendLen = currentClientConn.sendto(responseData,addr)
        except socket.error as message:
            logging.error('进程ID:%d - 文件描述符:%d - __epollOut()发送响应数据错误,原因:%s  下面将执行pass' % (self.pid, fd, message))
        else:
            responseParam['responseTime'] = time.time()
            self.clearFd(fd)
            logging.debug('%d - 发送完毕\n' % fd)
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

    '''
       清空fd相关连接和变量
    '''

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
