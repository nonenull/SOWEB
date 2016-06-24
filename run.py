# -*- coding:utf-8 -*-
import os,sys
from multiprocessing import Process
from System.server import Server
from Config.config import DAEMON

def forkNewProcess():
    p = Process(target=Server,args=())
    p.start()
    sys.exit(0)

def start():
    # 转为后台运行,并退出当前主进程
    if DAEMON:
        forkNewProcess()
    else:
        Server()

def stop():
    os.system("killall -r 'SOWEB'")

def restart():
    stop()
    start()

def status():
    num = os.popen('ps aux |grep "SOWEB"|grep -v grep |wc -l').read()
    if int(num) > 1:
        print('running')
    else:
        print('not running')


if __name__ == "__main__":
    try:
        arg = sys.argv[1]
    except IndexError:
        arg = None

    if arg == 'restart':
        stop()
        start()
    elif arg == 'stop':
        stop()
    elif arg == 'status':
        status()
    else:
        start()
