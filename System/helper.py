# -*- coding:utf-8 -*-
import os, sys, gzip
import traceback
from hashlib import md5
import StringIO
import re


class Helper:
    def __init__(self):
        self.actionDic = {}
        self.actionTime = {}

    def addSysPath(self):
        fileList = os.walk("./")
        for root, dirs, files in fileList:
            sys.path.append(root)

    def createPath(self):
        # 检查Static目录
        self.staticDirPath = "Static/"
        if not os.path.exists(self.staticDirPath):
            os.makedirs(self.staticDirPath)

        # 创建Cache目录,可以将缓存文件保存到Cache目录中
        self.cacheDirPath = "Cache/"
        if not os.path.exists(self.cacheDirPath):
            os.makedirs(self.cacheDirPath)

        # 创建Cache目录,可以将缓存文件保存到/dev/shm/Cache/内存中
        self.memoryCacheDirName = "/dev/shm/Cache/"
        if not os.path.exists(self.memoryCacheDirName):
            os.makedirs(self.memoryCacheDirName)

    def getTraceStackMsg(self):
        tb = sys.exc_info()[2]
        msg = ''
        for i in traceback.format_tb(tb):
            msg += i
        return msg

    def md5sum(fobj):
        m = md5.new()
        while True:
            d = fobj.read(65536)
            if not d:
                break
            m.update(d)
        return m.hexdigest()

    def responseGzip(self, responseText):
        buf = StringIO()
        f = gzip.GzipFile(mode='wb', fileobj=buf)
        f.write(responseText)
        f.close()

    # 删除文件中的 注释,空格,换行符,制表符
    def trimFile(self, file):
        fileFd = open(file)
        data = fileFd.read()

        # 设置 匹配注释 正则表达式
        annotationReg = re.compile('(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)')

        # 设置 匹配空格,换行符,制表符 正则表达式
        spaceReg = re.compile('\s+')

        # 去掉注释
        annotationTrimData = re.sub(annotationReg, '', data)

        # 再去掉 空格,换行符,制表符
        spaceTrimData = re.sub(spaceReg, '', annotationTrimData)
        fileFd.close()
        return spaceTrimData
