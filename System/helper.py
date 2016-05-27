# -*- coding:utf-8 -*-
import os, sys
import re


class Helper:
    def __init__(self):
        self.actionDic = {}
        self.actionTime = {}

    def addSysPath(self):
        fileList = os.walk("./Controller")
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



