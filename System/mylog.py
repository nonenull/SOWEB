# -*- coding: utf-8 -*-
import logging, logging.config, os
from sys import _getframe
from multiprocessing import Queue
from Config.config import LOG_LEVEL,DAEMON

class Mylog:
    def __init__(self):
        self.__LOG_PATH = 'logs'
        self.__LEVEL_ENUM = {
            'ERROR' : 0,
            'WARNING' : 1,
            'INFO' : 2,
            'DEBUG' : 3
        }
        self.__checkLogPath()
        self.__setLogConfig()
        logging.config.dictConfig(self.__LOGGING)

        self.__queue = Queue()

    def __setLogConfig(self):
        # log配置
        self.__LOGGING = {
            # 版本，总是1
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'},
                'simple': {'format': '%(levelname)s %(message)s'},
                'default': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                },
                'debugFile': {
                    'level': 'DEBUG',
                    # TimedRotatingFileHandler会将日志按一定时间间隔写入文件中，并
                    # 将文件重命名为'原文件名+时间戮'这样的形式
                    # Python提供了其它的handler，参考logging.handlers
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'formatter': 'default',
                    # 后面这些会以参数的形式传递给TimedRotatingFileHandler的
                    # 构造器

                    # filename所在的目录要确保存在
                    'filename': '%s/applog-debug.log'%self.__LOG_PATH,
                    # 刷新时间
                    'when': 'D',
                    'interval': 1,
                    'encoding': 'utf8',
                },
                'infoFile': {
                    'level': 'INFO',
                    # TimedRotatingFileHandler会将日志按一定时间间隔写入文件中，并
                    # 将文件重命名为'原文件名+时间戮'这样的形式
                    # Python提供了其它的handler，参考logging.handlers
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'formatter': 'default',
                    # 后面这些会以参数的形式传递给TimedRotatingFileHandler的
                    # 构造器

                    # filename所在的目录要确保存在
                    'filename': '%s/applog-info.log'%self.__LOG_PATH,
                    # 每5分钟刷新一下
                    'when': 'D',
                    'interval': 1,
                    'encoding': 'utf8',
                },
                'errorFile': {
                    'level': 'ERROR',
                    # TimedRotatingFileHandler会将日志按一定时间间隔写入文件中，并
                    # 将文件重命名为'原文件名+时间戮'这样的形式
                    # Python提供了其它的handler，参考logging.handlers
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'formatter': 'default',
                    # 后面这些会以参数的形式传递给TimedRotatingFileHandler的
                    # 构造器

                    # filename所在的目录要确保存在
                    'filename': '%s/applog-error.log'%self.__LOG_PATH,
                    'when': 'D',
                    'interval': 1,
                    'encoding': 'utf8',
                }
            },
            'loggers': {
                'debug': {
                    'level': 'DEBUG',
                    'handlers': self.__setHandlers('debug'),
                    'propagate': True
                },
                'info': {
                    'level': 'INFO',
                    'handlers': self.__setHandlers('info'),
                    'propagate': True
                },
                'error': {
                    'level': 'ERROR',
                    'handlers': self.__setHandlers('error'),
                    'propagate': True
                }
            }
        }

    def __checkLogPath(self):
        # 检查并保证logs目录存在
        if not os.path.exists(self.__LOG_PATH):
            os.makedirs(self.__LOG_PATH)

    #'handlers': ['console', 'debugFile'],
    def __setHandlers(self,level):
        handlers = []
        handlers.append('%sFile'%level)
        if not DAEMON:
            handlers.append('console')

        return handlers

    def __getStack(self,depth = 2):
        frame = _getframe(depth)
        code = frame.f_code
        moduleName = frame.f_globals.get('__name__')
        funcName = code.co_name
        lineNumber = code.co_firstlineno
        return '[%s.%s:%d] - ' % (moduleName, funcName, lineNumber)

    def info(self,*args):
        self.__queue.put_nowait(('info',args))

    def debug(self,*args):
        args = list(args)
        args.insert(0,self.__getStack())
        self.__queue.put_nowait(('debug',args))

    def error(self,*args):
        args = list(args)
        args.insert(0,self.__getStack())
        self.__queue.put_nowait(('error',args))

    def startLogHandles(self):
        while 1:
            level,args = self.__queue.get()
            logger = logging.getLogger(level)
            if self.__LEVEL_ENUM.get(LOG_LEVEL) >= self.__LEVEL_ENUM.get('INFO'):
                log = getattr(logger,level)
                log(' '.join(map(str,args)))

myLogging = Mylog()
