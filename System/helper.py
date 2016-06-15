# -*- coding:utf-8 -*-
import os, sys

class Helper:
    def __init__(self):
        # ctl 代表 controller
        self.ctlPath = "Controller"
        self.ctlImportDic = {}
        self.ctlModifyMTimeDic = {}
        self.staticDirPath = "Static/"
        self.cacheDirPath = "Cache/"
        self.memoryCacheDirName = "/dev/shm/Cache/"

    '''
        提前获取controller目录下的py文件,提前导入并记录文件修改时间
    '''
    def getControllerInfo(self):
        fileList = os.listdir(self.ctlPath)
        for file in fileList:
            filePath = os.path.join(self.ctlPath,file)
            if os.path.isfile(filePath) and not file.startswith(".") and file.endswith("py"):
                prefix,suffix = file.split(".")
                self.ctlImportDic[prefix] = __import__(prefix)
                self.ctlModifyMTimeDic[prefix] = os.path.getmtime(filePath)

    '''
        提前将项目目录加入sys.path
    '''
    def addSysPath(self):
        for path in os.listdir('./'):
            if os.path.isdir(path):
                sys.path.append(path)

    '''
        提前检查,创建好缓存和静态文件目录
    '''
    def createPath(self):
        # 检查Static目录
        if not os.path.exists(self.staticDirPath):
            os.makedirs(self.staticDirPath)

        # 创建Cache目录,可以将缓存文件保存到Cache目录中
        if not os.path.exists(self.cacheDirPath):
            os.makedirs(self.cacheDirPath)

        # 创建/dev/shm/Cache/目录,可以将缓存文件保存到内存中
        if not os.path.exists(self.memoryCacheDirName):
            os.makedirs(self.memoryCacheDirName)


