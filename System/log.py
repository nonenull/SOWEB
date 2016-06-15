# -*- coding: utf-8 -*-
import logging, logging.config,datetime
from sys import _getframe, exc_info
from traceback import format_tb
from Config.config import LOG_LEVEL

ENUM = {
'ERROR' : 0,
'WARNING' : 1,
'INFO' : 2,
'DEBUG' : 3
}

LOGGING = {
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
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
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
            'filename': 'logs/applog-debug.log',
            # 每5分钟刷新一下
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
            'filename': 'logs/applog-info.log',
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
            'filename': 'logs/applog-error.log',
            'when': 'D',
            'interval': 1,
            'encoding': 'utf8',
        }
    },
    'loggers': {
        'debug': {
            'level': 'DEBUG',
            'handlers': ['console', 'debugFile'],
            'propagate': True
        },
        'info': {
            'level': 'INFO',
            'handlers': ['console', 'infoFile'],
            'propagate': True
        },
        'error': {
            'level': 'ERROR',
            'handlers': ['console', 'errorFile'],
            'propagate': True
        }
    }
}
logging.config.dictConfig(LOGGING)
debugLogger = logging.getLogger('debug')
infoLogger = logging.getLogger('info')
errorLogger = logging.getLogger('error')

def getTraceStackMsg():
    tb = exc_info()[2]
    msg = ''
    for i in format_tb(tb):
        msg += i
    return msg


def getTrace():
    # 模块名
    moduleName = _getframe().f_back.f_back.f_globals.get('__name__')

    # 函数名
    funcName = _getframe().f_back.f_back.f_code.co_name  # 获取调用函数名

    # 行数
    lineNumber = _getframe().f_back.f_back.f_lineno  # 获取行号
    return '[%s.%s:%d] - ' % (moduleName, funcName, lineNumber)


def info(*args):
    if ENUM.get(LOG_LEVEL) >= ENUM.get('INFO'):
        infoLogger.info(' '.join(map(str,args)))

# DEBUG 输出 更多详细信息
def debug(*args):
    if ENUM.get(LOG_LEVEL) >= ENUM.get('DEBUG'):
        debugLogger.debug(getTrace() + ' '.join(map(str,args)))


def error(*args):
    if ENUM.get(LOG_LEVEL) >= ENUM.get('ERROR'):
        errorLogger.error(getTrace() + ' '.join(map(str,args)) + '\n' + getTraceStackMsg())
