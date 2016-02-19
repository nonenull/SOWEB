# -*- coding:utf-8 -*-

import os, sys, time, signal

def start():
    os.system('python run.py')

def stop():
    parentList = os.popen("ps -ef|grep 'python run.py'|grep -v grep|awk '{print $2}'").readlines()
    for pid in parentList:
        os.kill(int(pid), signal.SIGKILL)

def status():
    pass

if __name__ == "__main__":
    try:
        command = sys.argv[1]
    except Exception as e:
        print('缺少操作参数 (start, stop, restart, status).')
        sys.exit(0)

    if command == 'start':

        start()

    elif command == 'stop':

        stop()

    elif command == 'restart':

        stop()
        time.sleep(1)
        start()

    elif command == 'status':

        status()

    else:
        print('仅支持以下操作 (start, stop, restart, status). ')