# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
from Config.config import LOG_EXPIRATION_TIME,LOG_LEVEL

logDirPath = "logs"
logName = "applog"

logger = logging.getLogger()
logger.setLevel(getattr(logging,LOG_LEVEL))
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(module)s:%(message)s")

class Logger:

    def __init__(self,logLevel):
        # 如果日志目录不存在,新建一个
        self.__mkdirs()

        # 初始化日志 --- applog.debu
        self.baseFilename = "%s-%s.log" % (os.path.join(logDirPath, logName),logLevel)

        # 设置日志半夜切割
        fileHandler = logging.handlers.TimedRotatingFileHandler(self.baseFilename, when='midnight', interval=1, backupCount=LOG_EXPIRATION_TIME, encoding=None)
        # fileHandler.suffix = "%Y-%m-%d"
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

    def __mkdirs(self):
        if not os.path.exists(logDirPath):
            try:
                os.makedirs(logDirPath)
            except Exception as e:
                print(str(e))

    def info(self,msg):
        logger.info(msg)

    def warn(self,msg):
        logger.warn(msg)

    def debug(self,msg):
        logger.debug(msg)

    def error(self,msg):
        logger.error(msg)

def add(logLevel,param='',msg=''):
    entireLog = '%s %s'%(str(param),msg)
    Logger(logLevel).info(entireLog)

def info(msg):
    Logger('info').info(msg)


def warn(msg):
    Logger('warn').warn(msg)


def debug(msg):
    Logger('debug').debug(msg)


def error(msg):
    Logger('error').error(msg)
