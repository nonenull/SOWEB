# -*- coding: utf-8 -*-
import os, sys, socket
from setproctitle import setproctitle
from multiprocessing import cpu_count,Process
from  Config.config import HOST, PORT, BACKLOG, PROCESSES_NUM
from System.mylog import myLogging as logging
from System.core import Epoll

class Server:
    def __init__(self):
        # 初始化进程名称 序号
        self.processNameNum = 1

        # 设置进程名
        setproctitle('SOWEB: master process %s'%self.getFullPath())

        # 创建socket监听服务
        self.createSocketServer()

        # 创建子进程
        self.createChildProcessing()

        # 开始日志处理器
        logging.startLogHandles()

    def createSocketServer(self):
        try:
            # 创建socket套接字
            # socket.SOCK_STREAM 流式socket
            # socket.AF_INET 服务器之间网络通信
            self.serverFd = serverFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverFd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # 将套接字绑定到地址, 在AF_INET下,以元组（host,port）的形式表示地址.
            serverFd.bind((HOST, PORT))

            # 开始监听TCP传入连接。backlog指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。
            serverFd.listen(BACKLOG)

            # 如果flag为0，则将套接字设为非阻塞模式，否则将套接字设为阻塞模式（默认值）。非阻塞模式下，如果调用recv()没有发现任何数据，或send()调用无法立即发送数据，那么将引起socket.error异常。
            serverFd.setblocking(0)
            # serverFd.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        except socket.error as message:
            # print('监听服务失败,请检查端口冲突,或者查看是否重复运行 %s' % message)
            logging.error('监听服务失败,请检查端口冲突,或者查看是否重复运行 %s' % message)
            sys.exit(0)

    def createChildProcessing(self):

        # 如果config.PROCESSES_NUM设置为0, 按照CPU核心数量来创建子进程
        if not PROCESSES_NUM:
            num = cpu_count()
        else:
            num = PROCESSES_NUM
        for i in range(num):
            self.forkProcess()
            self.processNameNum = self.processNameNum + 1


    def forkProcess(self):
        print('create')
        # 创建工作子进程
        p = Process(target=self.initProcess, args=())
        p.daemon = True
        p.start()

    def initProcess(self):
        setproctitle('SOWEB: worker process %d'%self.processNameNum)
        Epoll(self.serverFd)

    def getFullPath(self):
        pwd = ''
        arg = sys.argv[0]
        argSplit = arg.split('/')
        file = argSplit[-1]
        if os.path.isfile(file):
            pwd = os.getcwd()
        return os.path.join(pwd, file)
