# -*- coding:utf-8 -*-

import socket, sys, select, errno, threading, time, Queue, signal, os
import compileall, sendfile
from multiprocessing import Process, cpu_count

from Config import config
import log as logger
from webapi import WebApi
from helper import Helper

# 强制utf8
reload(sys)
sys.setdefaultencoding('utf8')

# 执行Helper类中的初始准备工作
Helper = Helper()
Helper.addSysPath()

class WorkTasksThread(threading.Thread):
    def __init__(self, threadCondition, queue, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.threadCondition = threadCondition
        self.queue = queue
        self.setDaemon(True)

    def processer(self, args, kwargs):
        try:
            self.worker = WebApi()
            param = args[0]
            epollFd = args[1]
            fd = args[2]

            # 处理请求，并生成response数据
            self.worker.process(param, epollFd, fd)
        except Exception as e:
            logger.error("worker job error:" + Helper.getTraceStackMsg())

    def run(self):
        while True:
            try:
                args, kwargs = self.queue.get()
                self.processer(args, kwargs)
            except Queue.Empty:
                continue
            except:
                logger.error("worker thread error:" + Helper.getTraceStackMsg())


class TimeoutTasksThread(threading.Thread):
    def __init__(self, threadCondition, queue, **kwargs):
        threading.Thread.__init__(self, kwargs=kwargs)
        self.threadCondition = threadCondition
        self.queue = queue
        self.setDaemon(True)

    def processer(self, args, kwargs):
        connParam = args[0]
        fd = args[1]
        while (connParam.get('time') > time.time()):
            pass
        logger.debug('已经超时')
        # print connParam

    def run(self):
        while True:
            try:
                args, kwargs = self.queue.get()
                self.processer(args, kwargs)
            except Queue.Empty:
                continue
            except:
                logger.error("timeout thread error:" + Helper.getTraceStackMsg())


class ThreadPool:
    def __init__(self, numOfThreads=10, role=''):
        self.threadCondition = threading.Condition()
        self.role = role
        self.queueName = role + '_queue'

        # self.queue = Queue.Queue()
        setattr(self, self.queueName, Queue.Queue())

        self.threads = []
        self.__createThreadPool(numOfThreads)

    # 创建线程
    def __createThreadPool(self, numOfThreads):
        for i in range(numOfThreads):
            if self.role == 'timeout':
                thread = TimeoutTasksThread(self.threadCondition, getattr(self, self.queueName))
            else:
                thread = WorkTasksThread(self.threadCondition, getattr(self, self.queueName))
            self.threads.append(thread)

    def start(self):
        for thread in self.threads:
            thread.start()

    def addJob(self, *args, **kwargs):
        # self.role + '_queue'.put((args, kwargs))
        getattr(self, self.queueName).put((args, kwargs))


class Epoll:
    def __init__(self, serverFd):
        self.serverFd = serverFd
        self.serverFdFileNo = self.serverFd.fileno()
        self._connParams = {}
        self.childProcess = {}

        #创建线程池，用于搞定超时的问题
        # self.timeOutThreadPool = ThreadPool(2,'timeout')
        # self.timeOutThreadPool.start()

        # 创建线程池
        self.workerThreadPool = ThreadPool(config.THREADS_NUM)
        self.workerThreadPool.start()

        # 1 创建epoll,注册事件
        self.createEpoll()

        # 2 开始处理事件
        self.epollEventHandle()

    def createEpoll(self):
        # 开始EPOLL处理
        try:
            # 创建epoll并且注册事件
            self.epollFd = epollFd = select.epoll(config.WORKER_CONNECTIONS)
            epollFd.register(self.serverFdFileNo, select.EPOLLIN)
        except select.error as message:
            logger.error('epoll注册事件错误 %s', message)

    def epollEventHandle(self):
        dict = {select.EPOLLIN:self.__epollIn, select.EPOLLOUT:self.__epollOut,select.EPOLLHUP:self.clearFd, select.EPOLLERR:self.clearFd}
        try:
            while 1:
                events = self.epollFd.poll()
                # 死循环 实时获取epoll中的数据
                for fileNo, event in events:
                    dict.get(event,self.clearFd)(fileNo)
        except TypeError:
            pass
            # logger.debug('%d event: %d select.EPOLLERR: %d %s %s'%(fileNo, event,select.EPOLLERR, e, str(dict)))

    # 创建与客户端的连接
    def __epollIn(self, fd):

        if fd == self.serverFdFileNo:
            try:
                # 获取当前时间戳
                linkStartTime = time.time()

                # 等待从连接队列中抽取连接
                clientConn, clientAddr = self.serverFd.accept()

                # 设置新的socket连接为非阻塞
                clientConn.setblocking(0)
                clientConn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # 将 conn 和 addr 信息分别保存起来
                clientFd = clientConn.fileno()

                self._connParams[clientFd] = {"addr": clientAddr, "connections": clientConn, "time": linkStartTime}

                # self.timeOutThreadPool.addJob(self._connParams[clientFd], fd)

                # 向 epoll 句柄中注册 连接 socket 的 可读 事件
                self.epollFd.register(clientFd, select.EPOLLET | select.EPOLLIN)
            except socket.error:
                pass

        else:
            # 根据config配置决定是否更新pyc文件
            # if config.AUTO_RELOAD:
            #     compileall.compile_dir(r'./', quiet=1)

            # 获取抓到的socket连接的信息
            connParam = self._connParams.get(fd)

            # 如果此条连接的数据为空，不处理跳过
            if not connParam:
                return

            # 开始接收数据
            totalDatas = ''
            while 1:
                try:
                    # connParam['connections'].settimeout(5)
                    # 从激活的连接上接收数据
                    data = connParam['connections'].recv(config.BUFFER_SIZE)

                    # 若接受到的是空数据，断开连接
                    if not data:
                        self.clearFd(fd)
                        break
                    else:
                        # 有数据的话，将接收到的数据拼接保存在datas 中
                        totalDatas += data
                        # logger.debug('测试发送了多少请求:  %s'%totalDatas)

                except socket.error as message:
                    # 在 非阻塞 socket 上进行 recv 需要处理 读穿 的情况
                    # 这里实际上是利用 读穿 出 异常 的方式跳到这里进行后续处理
                    if message.errno == errno.EAGAIN:
                        # 将已接收数据保存起来
                        connParam['requestData'] = totalDatas
                        self.workerThreadPool.addJob(connParam, self.epollFd, fd)
                    else:
                        # 出错处理
                        self.clearFd(fd)
                        logger.error('EPOLLIN接收数据错误 %s' % message)
                    break

    # 发送响应数据
    def __epollOut(self, fd):

        # 获取连接数据
        responseParam = self._connParams.get(fd)

        # 获取响应数据
        responseData = responseParam.get('responseData')

        #
        if responseData == None:
            self.clearFd(fd)
            logger.error('获取不到响应数据 %s' % str(responseParam))

        currentSockConn = responseParam['connections']

        try:
            # 将之前收到的数据发回 client -- 通过 sendLen 来控制发送位置
            currentSockConn.sendall(responseData)
        except socket.error as message:
            logger.error(message)
            pass

        if not responseParam.get('keepalive', None):
            self.clearFd(fd)
        else:
            # 更新 epoll 句柄中连接 fd 注册事件为 可读
            self.epollFd.modify(fd,select.EPOLLET|select.EPOLLIN)
        # logger.debug('%s       %s    %d   pid: %d time: %f' % (str(responseParam['addr']), responseParam['responseData'][:15], responseParam['responseTextLen'], os.getpid(), (time.time() - responseParam.get('time')) ))
        logger.add('debug','%s       %s    %d   pid: %d time: %f' % (str(responseParam['addr']), responseParam['responseData'][:15], responseParam['responseTextLen'], os.getpid(), (time.time() - responseParam.get('time')) ))

    # 清空fd相关连接和变量
    def clearFd(self, fd):
        try:
            param = self._connParams[fd]
            self.epollFd.unregister(fd)
            param.get('connections').close()
            del self._connParams[fd]
        except socket.error as message:
            logger.debug('clearFd错误  %s %s'%(str(param),message))
            pass


class Run:
    def __init__(self):

        # 1 设置日志级别
        self.setLogLevel()

        # 2 创建socket监听服务
        self.createSocketServer()

        # 3 创建子进程
        self.createChildProcessing()

        # 如果有子进程退出,重新创建子进程
        # signal.signal(signal.SIGCHLD, self.createChildProcessing)

        if config.DAEMON:
            # 转为后台运行
            mainPid = os.getpid()
            os.system('kill -HUP %d' % mainPid)
        else:
            signal.pause()

    def createSocketServer(self):
        try:
            # 创建socket套接字
            # socket.SOCK_STREAM 流式socket
            # socket.AF_INET 服务器之间网络通信
            self.serverFd = serverFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverFd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 将套接字绑定到地址, 在AF_INET下,以元组（host,port）的形式表示地址.
            serverFd.bind((config.HOST, config.PORT))

            # 开始监听TCP传入连接。backlog指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。
            serverFd.listen(config.LISTEN)

            # 如果flag为0，则将套接字设为非阻塞模式，否则将套接字设为阻塞模式（默认值）。非阻塞模式下，如果调用recv()没有发现任何数据，或send()调用无法立即发送数据，那么将引起socket.error异常。
            serverFd.setblocking(0)

        except socket.error as message:
            logger.error('监听服务失败,请检查端口冲突 %s' % message)
            sys.exit(0)

    def setLogLevel(self):
        # 设置日志级别
        logLevel = ('ERROR', 'WARNING', 'INFO', 'DEBUG')
        count = len(logLevel) - 1
        logIndex = logLevel.index(config.LOG_LEVEL)
        while logIndex < count:
            logIndex = logIndex + 1
            logAttribute = 'is_%s' % logLevel[count].lower()
            setattr(logger.Logger(), logAttribute, False)

    def createChildProcessing(self):
        # 如果config.PROCESSES_NUM设置为0, 按照CPU核心数量来创建子进程
        if not config.PROCESSES_NUM:
            num = cpu_count()
        else:
            num = config.PROCESSES_NUM

        # 创建工作子进程
        for i in xrange(num):
            p = Process(target=Epoll, args=(self.serverFd,))
            p.daemon = False
            p.start()
