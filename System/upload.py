# -*- coding:utf-8 -*-
from Config import upload_config
from System.mylog import myLogging as logging
import os

class UploadCheckError(BaseException):
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class Upload:
    def __init__(self, fileData, config):
        self.postParamsDic = {}
        self.__filename, self.__content = fileData
        self.__filename = self.__filename.lower()
        self.__config = {}
        self.__generateConfig(config)
        # 对上传文件做判断,如果有错误直接引发异常
        self.__check()
        # 没问题开始上传文件
        self.__save()

    '''
        生成配置
    '''

    def __generateConfig(self, config):
        for key in dir(upload_config):
            key = key.upper()
            # 过滤内置变量
            if '__' in key:
                continue

            # 判断config中是否自定义了配置,如果有应用自定义的,没有用默认配置文件中的
            value = config.get(key)
            if value:
                self.__config[key] = value
            else:
                self.__config[key] = getattr(upload_config, key)

    '''
        判断没有
    '''

    def __check(self):
        # 获取后缀
        fileNameSuffix = self.__filename.split('.')[-1]
        if fileNameSuffix not in self.__config.get('ALLOWED_FILE_SUFFIX'):
            raise UploadCheckError('不允许上传的文件类型')

        if len(self.__content) > self.__config.get('MAX_SIZE'):
            raise UploadCheckError('文件大小超出限制')

    def __save(self):
        path = self.__config['PATH']
        # 上传的主目录在Upload下,判断自定义的路径是否包含主目录,没有的话组合路径,有就不组合
        # 如果自定义的路径中不包含主目录
        if path.find(upload_config.PATH) == -1:
            path = os.path.join(os.path.normpath(upload_config.PATH), os.path.normpath(path))

        # 判断path是否存在,不在创建
        if not os.path.exists(path):
            os.makedirs(path)

        # 如果有前缀,加上
        filePrefix = self.__config['FILE_PREFIX']
        if filePrefix:
            self.__filename = filePrefix + self.__filename
        logging.debug('path', path)
        fullPath = os.path.join(path, self.__filename)
        logging.debug('fullPath', fullPath)
        # logging.debug('repr=================',repr(self.__content))
        with open(fullPath,'wb') as fd:
            fd.write(self.__content.encode('ISO-8859-1'))
        logging.debug('上传啦傻逼')
