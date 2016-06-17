# -*- coding:utf-8 -*-

import time, os, socket, select
from Config import config
from System import log as logging
from System.threadwork import ThreadPool

class Epoll:
    def __init__(self, serverFd):
        self.serverFd = serverFd
        self.serverFdFileNo = serverFd.fileno()
        self.__connParams = {}
        self.childProcess = {}
        self.pid = os.getpid()
        # self.workerPool = ThreadPool(config.THREADS_NUM)

        # 初始化线程
        self.workerThread = ThreadPool(config.THREADS_NUM)
        self.workerThread.start()

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
                # 死循环 实时获取epoll中的事件
                for fileNo, event in events:
                    eventsDict.get(event, self.clearFd)(fileNo)

        except KeyError as message:
            # 变量dict以外的事件不处理
            logging.error(
                '进程ID:%d - epollEventHandle() - 事件超出范围 - 错误代码: %s ' % (self.pid, message))

        finally:
            pass

    '''
     处理与客户端的连接
    '''

    def __epollIn(self, fd):
        # 如果fd等于serverFdFileNo,说明是服务端监听socket有事件发生
        if fd == self.serverFdFileNo:
            try:
                clientConn, clientAddr = self.serverFd.accept()
                # 设置新的socket连接为非阻塞
                clientConn.setblocking(0)
                clientConn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # 获取新连接的文件描述符
                clientFd = clientConn.fileno()
                logging.debug('accept到新的client连接 -%d %s' % (clientFd, clientAddr))
                acceptTime = time.time()
                self.__connParams[clientFd] = {"addr": clientAddr, "connections": clientConn, "acceptTime": acceptTime}
                # 向 epoll 句柄中注册 连接 socket 的 可读 事件
                self.epollFd.register(clientFd, select.EPOLLET | select.EPOLLIN)
            except socket.error:
                # 因为是多个进程竞争,所以其它进程会收到socket错误,需要忽略掉
                pass

        else:
            # 获取抓到的socket连接的信息
            connParam = self.__connParams.get(fd)
            # 开始接收数据
            totalDatas = ''
            try:
                while 1:
                    data = connParam['connections'].recv(config.RCV_BUFFER_SIZE)
                    # 当客户端主动断开连接,recv会直接返回b'',所以这里需要判断一下,否则会陷入死循环
                    if not data: break
                    totalDatas += data.decode('utf-8')
            except socket.error:
                # 在non-block的情况下,recv数据完成后会产生一个errno 11 的异常
                # 在同时打开多个进程的情况下,recv数据完成后会产生一个errno 11 的异常
                pass
            # 判断数据是否符合HTTP 规范
            if '\r\n\r\n' not in totalDatas:
                self.clearFd(fd)
                logging.debug('接受到的数据不正常', fd, totalDatas)
                return

            connParam['requestData'] = totalDatas
            connParam['recvTime'] = time.time()
            self.workerThread.addJob(self.epollFd, fd, connParam)

    '''
        发送响应数据
    '''

    def __epollOut(self, fd):
        logging.debug('%d - %d -  开始send数据 -----------' % (fd, self.pid))
        # print self.__connParams,self.__connParams.get(fd)
        # 获取连接数据
        responseParam = self.__connParams.get(fd)

        # 获取响应数据
        responseData = responseParam.get('responseData')
        logging.debug('=====', responseData)
        if not responseData:
            logging.error('responseData为空  %d将执行clearFd() ' % fd)
            self.clearFd(fd)
            return

        currentClientConn = responseParam['connections']
        try:
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
        #     #     self.__connParams[fd] = {"addr": responseParam['addr'],
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
            param = self.__connParams[fd]
            param.get('connections').shutdown(socket.SHUT_RDWR)
            param.get('connections').close()
            del self.__connParams[fd]
        except socket.error as message:
            logging.error('clearFd错误 %s' % (message))
            pass
