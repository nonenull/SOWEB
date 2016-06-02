# -*- coding:utf-8 -*-

from StringIO import StringIO
from urlparse import parse_qs
from Cheetah.Template import Template
import os, sys, re, cgi, time, gzip, socket
from helper import Helper
from Config.config import CONTROLLER, CONTENT_TYPE, STATUS, KEEP_ALIVE,KEEP_ALIVE_TIMEOUT, CACHE_TIME, GZIP, GZIP_LEVEL, \
    GZIP_MIN_LENGTH, GZIP_TYPES, TRIM, \
    TRIM_TYPES, CHUNKED_MIN_LENGTH
import select
import log as logging

Helper = Helper()
Helper.createPath()
# 执行Helper类
_actionDic = Helper.actionDic
_actionTime = Helper.actionTime
_staticDirPath = Helper.staticDirPath
_cacheDirPath = Helper.cacheDirPath
_memoryCacheDirPath = Helper.memoryCacheDirName


class WebApi:
    def __init__(self, epollFd, fd, connParam=''):
        logging.debug('%d - 开始解析http请求'%fd)

        # 请求头
        self.requestHeaders = {}

        # 初始化response 信息
        self.httpVersion = 'HTTP/1.1'
        self.requestUri = '/'

        # 初始化响应头
        self.responseHeaders = {}
        self.responseStatus = 200
        self.responseText = ''
        self.responseHeaders["Content-Type"] = 'text/html'
        if KEEP_ALIVE:
            self.responseHeaders["Connection"] = 'keep-alive'
            self.responseHeaders['Keep-Alive'] = 'timeout=%d' % KEEP_ALIVE_TIMEOUT
        else:
            self.responseHeaders["Connection"] = 'close'

        # 设置默认的控制器
        self.controller = CONTROLLER
        # 默认action
        self.action = 'index'

        self.getDic = {}
        self.form = None
        self.postDic = {}
        self.connParam = connParam
        self.__epollFd = epollFd
        self.__clientFd = fd
        # 开始响应过程
        if connParam:
            self.process(connParam)

    # 解析请求数据
    def parse(self, requestData):
        '''
            GET /fuck HTTP/1.1
            Host: 172.16.190.132:8888
            User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
            Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
            Accept-Encoding: gzip, deflate
            Connection: keep-alive
            Cache-Control: max-age=0


        '''
        logging.debug(requestData)
        headend = requestData.find("\r\n\r\n")
        rfile = ""
        logging.debug(headend)
        if headend > 0:
            rfile = requestData[headend + 4:]
            headList = requestData[0:headend].split("\r\n")
        else:
            headList = requestData.split("\r\n")

        self.rfile = StringIO(rfile)
        headerFirstLine = headList.pop(0)
        # _logger.debug('第一行 %s'%headerFirstLine)

        # 按照空格切割 ‘GET /fuck HTTP/1.1’
        self.requestMethod, self.requestUri, self.httpVersion = re.split('\s+', headerFirstLine)

        # 根据?切割,有get参数的情况下 /controller/action?xxx=xxx
        splitRequestUri = self.requestUri.split('?')

        # 如果大于1,说明?后面有get参数
        if len(splitRequestUri) > 1:
            self.baseUri, self.paramStr = splitRequestUri
        else:
            # /controller/action
            self.baseUri = splitRequestUri[0]
            self.requestParamStr = None

        splitRequestUri = self.baseUri.split('/')
        self.__filePrefixName, self.__fileExtName = os.path.splitext(splitRequestUri[-1])

        # 截取controller和action
        self.__getControllerAndAction(splitRequestUri)

        for item in headList:
            # 过滤空行
            if item.strip() == "":
                continue

            # 获取key的索引值
            segindex = item.find(":")

            if segindex < 0:
                continue
            key = item[0:segindex].strip()
            value = item[segindex + 1:].strip()
            self.requestHeaders[key] = value

        methodLower = self.requestMethod.lower()

        if methodLower == "get" and "?" in self.requestUri:
            # 获取?后面的的参数和值
            if self.getDic:
                self.getDic = dict(parse_qs(self.paramStr), **self.getDic)
            else:
                self.getDic = parse_qs(self.paramStr)

        elif methodLower == "post" and self.responseHeaders.get('Content-Type', "").find("boundary") > 0:
            # 判断是否有上传文件
            self.form = cgi.FieldStorage(fp=self.rfile, headers=None,
                                         environ={'REQUEST_METHOD': self.requestMethod,
                                                  'CONTENT_TYPE': self.responseHeaders['Content-Type'], })
            if self.form == None:
                self.form = {}
        elif methodLower == "post":
            self.postDic = parse_qs(rfile)

    #
    def __getControllerAndAction(self, splitRequestUri):
        # 删除所有元素
        while '' in splitRequestUri:
            splitRequestUri.remove('')

        splitRequestUriLen = len(splitRequestUri)

        # logging.debug('splitRequestUriLen %d ' % splitRequestUriLen)
        # 有controller和action或者GET param的情况
        if splitRequestUriLen >= 2:

            # 获取controller和action，并删除，剩下的就是GET参数
            self.controller = splitRequestUri.pop(0)
            # logging.debug('splitRequestUriLen %s ' % str(splitRequestUri))
            self.action = splitRequestUri.pop(0)
            # logging.debug('splitRequestUriLen %s ' % str(splitRequestUri))
            i = 1
            for param in splitRequestUri:
                if param.strip() is not '':
                    self.getDic[i] = param
                    i = i + 1

        elif splitRequestUriLen == 1:
            self.controller = splitRequestUri[0]
            self.action = 'index'

        else:
            self.controller = 'index'
            self.action = 'index'

    # 删除文件中的 注释,空格,换行符,制表符
    def trim(self, file):
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

    def input(self, method=None):
        if method == 'get':
            return self.getDic
        elif method == 'post':
            return self.postDic
        else:
            return dict(self.getDic, **self.postDic)

    def render(self, file, data={}):
        renderPath = 'View/'
        prefixName, extName = os.path.splitext(file)
        if extName != '.html':
            templateHtml = Template(file=renderPath + file + '.html')
        else:
            templateHtml = Template(file=renderPath + file)

        # 遍历data，设置模板变量
        for k, v in data.iteritems():
            # 相当于 templateHtml.{k}={v}
            setattr(templateHtml, k, v)

        return templateHtml

    def __sendResponseFile(self):

        # 判断静态文件是否存在
        def isStaticFileExist():
            if not os.path.exists(staticFileFullPath):
                self.fastResponse(404)

        # 判断缓存文件是否存在
        def isCacheDirExist():
            dir, filename = os.path.split(cacheFileFullPath)
            if not os.path.exists(dir):
                os.makedirs(dir)

        # 过去时间和文件修改时间做对比，相等就是文件没有修改过,返回304
        def isFileCacheExpiry():
            if lastTimeStr == fileModifyTimeStr and "Range" not in self.requestHeaders:
                self.responseStatus = 304
                self.responseHeaders['Last-Modified'] = fileModifyTimeStr
                self.responseHeaders['ETag'] = fileModifyTime
                self.responseHeaders['Date'] = currentTimeStr

        # 初始化部分Header
        def initHeader():
            self.responseHeaders['Last-Modified'] = fileModifyTimeStr
            self.responseHeaders['ETag'] = fileModifyTime
            self.responseHeaders['Date'] = currentTimeStr

            # 设置Content-Type
            contentType = CONTENT_TYPE.get(extName)
            if contentType:
                self.responseHeaders['Content-Type'] = contentType

            # 根据配置设置缓存时间
            if CACHE_TIME == 0:
                self.responseHeaders['Cache-Control'] = 'no-cache'
            else:
                self.responseHeaders['Cache-Control'] = 'max-age=%d' % CACHE_TIME

        # 判断是否需要删除空格和换行符
        def isNeedTrim():
            # 如果配置了TRIM,自动去除html,css,js中的注释以及重复的空白符（\n，\r，\t，' '）,否则直接读取静态文件
            if TRIM and self.responseHeaders.get('Content-Type') in TRIM_TYPES:
                if not os.path.exists(self.__trimFileFullPath) or os.path.getmtime(
                        self.__trimFileFullPath) < fileModifyTime:
                    trimFileData = self.trim(staticFileFullPath)
                    trimFileFd = open(self.__trimFileFullPath, 'w')
                    trimFileFd.write(trimFileData)
                    trimFileFd.close()
                return True
            else:
                return False

        # 判断是否需要gzip压缩
        def isNeedGzip():
            # 判断配置中gzip是否已开启,且请求文件在允许gzip压缩的列表中
            if self.responseHeaders.get('Content-Type') in GZIP_TYPES and GZIP:
                # 如果gzip缓存文件不存在或者已经过期,重新生成
                if not os.path.exists(self.__gzipFileFullPath) or os.path.getmtime(
                        self.__gzipFileFullPath) < fileModifyTime:
                    if TRIM:
                        file = self.__trimFileFullPath
                    else:
                        file = staticFileFullPath

                    staticFileFd = open(file)
                    staticFileData = staticFileFd.read()
                    staticFileFd.close()

                    # gzip格式创建缓存文件，读取静态资源文件写入缓存
                    gZipFileFd = gzip.open(self.__gzipFileFullPath, 'wb')
                    gZipFileFd.write(staticFileData)
                    gZipFileFd.close()

                # 添加一个response头显示资源已经gzip压缩
                self.responseHeaders['Content-Encoding'] = 'gzip'
                return True
            else:
                return False

        # 处理分段传输,断点续传
        def rangeResponse():
            rangeValue = self.requestHeaders["Range"].strip(' \r\n')
            rangeValue = rangeValue.replace("bytes=", "")

            # 获取请求数据的范围
            rangeStart, rangeEnd = rangeValue.split('-')

            # 如果范围rangeEnd为空，则rangeEnd修改为文件大小(因为初始是0，所以大小-1)
            if rangeEnd == '':
                rangeEnd = fileSize - 1

            rangeStart = int(rangeStart)
            rangeEnd = int(rangeEnd)

            self.responseHeaders['Accept-Ranges'] = 'bytes'
            self.responseStatus = 206
            self.responseHeaders['Content-Range'] = 'bytes %s-%s/%s' % (rangeStart, rangeEnd, fileSize)
            # 偏移量
            offset = rangeStart

            # 请求的分段数据总长度
            partLen = rangeEnd - rangeStart + 1
            # logging.debug('长度 %d' % partLen)

            if partLen < 0:
                partLen = 0

            self.responseHeaders['Content-Length'] = partLen

            staticFile = open(staticFileFullPath)

            # 设置文件的当前位置偏移,从偏移量开始读取数据
            staticFile.seek(offset)
            readlen = 10240
            if readlen > partLen:
                readlen = partLen

            firstdata = staticFile.read(readlen)
            self.responseText += firstdata
            partLen -= len(firstdata)

        def generateResponseText():
            staticFileData = staticFile.read()
            bufferSize = fileSize/4
            beginOffset = 0
            endOffset = bufferSize
            first = True
            if chunked:
                while 1:
                    offsetData = staticFileData[beginOffset:endOffset]

                    # 取data长度的16进制
                    offsetDataLen = hex(bufferSize)[2:]
                    if self.responseText:
                        self.responseText = '%s%s\r\n%s\n' % (self.responseText, offsetDataLen, offsetData)
                    else:
                        self.responseText = '%s\n%s\r\n' % (offsetDataLen, offsetData)

                    beginOffset = endOffset
                    endOffset = beginOffset + bufferSize

                    if endOffset > fileSize:
                        endOffset = fileSize
                        bufferSize = endOffset - beginOffset
                    elif endOffset == fileSize:
                        break

            else:
                self.responseText = staticFileData


        '''
         逻辑由此开始
        '''
        try:
            staticFile = None
            chunked = None
            # 获取静态文件路径
            staticFileFullPath = self.baseUri[self.baseUri.find(_staticDirPath) + 0:]

            # 获取缓存文件路径
            cacheFileFullPath = _memoryCacheDirPath + staticFileFullPath[7:]

            isCacheDirExist()

            self.__trimFileFullPath = cacheFileFullPath + '-trim'
            self.__gzipFileFullPath = cacheFileFullPath + '-gzip'

            # 判断文件是否存在,不存在报404
            isStaticFileExist()

            # 过期时间
            lastTimeStr = self.requestHeaders.get("If-Modified-Since", None)

            # 获取文件修改时间
            fileModifyTime = os.path.getmtime(staticFileFullPath)

            # 把文件修改时间转换为格林威治(GMT)时间
            fileModifyTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(fileModifyTime))

            # 把当前时间转换为格林威治(GMT)时间
            currentTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))

            # 检查缓存是否到期
            isFileCacheExpiry()

            # 后缀去掉.符号
            extName = self.__fileExtName.replace('.', '')

            # 初始化部分Header
            initHeader()

            # 判断是否缓存trim文件
            isTrim = isNeedTrim()

            # 判断是否缓存gzip文件
            isGzip = isNeedGzip()

            # logging.debug('Header %s'%str(self.responseHeaders))

            if isGzip:
                staticFileFullPath = self.__gzipFileFullPath
            elif isTrim:
                staticFileFullPath = self.__trimFileFullPath

            # 获取文件大小
            fileSize = os.path.getsize(staticFileFullPath)
            '''
             随着SNDBUF增大，send()返回已发送字节越大。接收窗口大小对结果影响不是线性的。实际已接收的只有窗口大小。
             在no blocking的情况下,发送的数据大于缓存区会导致客户端只能接受到部分数据
             如果文件大小大于1M,设置当前socket的发送缓冲区为fileSize的一半
            '''
            if fileSize > CHUNKED_MIN_LENGTH and CHUNKED_MIN_LENGTH > 0:
                self.responseHeaders['Transfer-Encoding'] = 'chunked'
                chunked = True
                self.connParam['connections'].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, fileSize*2)
                self.connParam['connections'].setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)

            # 打开文件
            staticFile = open(staticFileFullPath)

            # Range 只请求实体的一部分，指定范围 ---- 即断点续传
            if "Range" in self.requestHeaders:
                rangeResponse()
            else:
                generateResponseText()

        except OSError as message:
            self.fastResponse(404)
            logging.error(message)

        except Exception as message:
            self.fastResponse(500)
            logging.error(message)
        else:
            self.__startResponse()
        finally:
            if staticFile:
                staticFile.close()
            pass

    # 处理
    def process(self, connParam):
        requestData = connParam['requestData']
        logging.debug('@@@@@@@@@@@@@@',requestData,'@@@@@@@@@@@@')
        try:
            # 开始解析request header
            if requestData.strip() != '':
                self.parse(requestData)
            else:
                logging.debug('NONONONONONONONONONONONONO')
                self.fastResponse(500)
                return

            # 判断是否请求网站图标
            if self.requestUri == "/favicon.ico":
                self.requestUri = "/" + _staticDirPath + self.requestUri

            # 判断是否静态文件，判断URI是否含有Cache，Static或者favicon.ico,如果为True,不往后执行
            if _staticDirPath in self.requestUri or "favicon.ico" in self.requestUri:
                self.__sendResponseFile()
                return
            # 开始处理动态内容
            controller = _actionDic.get(self.controller)

            # 判断URL中没有controller的情况
            if controller == None:
                controller = __import__(self.controller)
                mtime = os.path.getmtime("Controller/%s.py" % self.controller)
                _actionTime[self.controller] = mtime
                _actionDic[self.controller] = controller

            else:
                loadTime = _actionTime[self.controller]
                mtime = os.path.getmtime("Controller/%s.py" % self.controller)
                if mtime > loadTime:
                    controller = reload(sys.modules[self.controller])
                    _actionTime[self.controller] = mtime
                    _actionDic[self.controller] = controller

            # controller.action
            action = getattr(controller, self.action)

            # 获取返回值
            actionReturn = action(self)
            if actionReturn:
                self.responseText = str(actionReturn)

            # 如果配置了gzip,且大小超过1K
            if GZIP and len(self.responseText) > GZIP_MIN_LENGTH:
                buf = StringIO()
                f = gzip.GzipFile(mode='wb', fileobj=buf, compresslevel=GZIP_LEVEL)
                f.write(self.responseText)
                f.close()
                # self.responseText = gzip.GzipFile(data=self.responseText, compresslevel=8)

            self.__startResponse()
        except ImportError as message:
            self.fastResponse(404)
            logging.error(message)
            pass
        except Exception as message:
            self.fastResponse(500)
            logging.error(message.args, message)
        finally:
            pass

    # 拼接Header，响应报文
    def __startResponse(self):
        try:

            self.responseHeaders["Content-Type"] = self.responseHeaders["Content-Type"] + ';charset=utf-8'

            # 例如 403 Forbidden
            httpStatus = "%d %s" % (self.responseStatus, STATUS.get(self.responseStatus))
            headStr = ''

            # 获取响应内容长度
            responseTextLen = len(self.responseText)


            # Transfer-Encoding 和 Content-Length 不可共存
            if not self.responseHeaders.has_key('Transfer-Encoding'):
                self.responseHeaders["Content-Length"] = responseTextLen

            self.connParam['responseTextLen'] = responseTextLen

            # 拼接Header
            for key in self.responseHeaders:
                headStr += "%s: %s\r\n" % (key, self.responseHeaders[key])

            # 拼接完整response
            self.connParam['responseData'] = "%s %s\r\n%s\n%s" % (
                self.httpVersion, httpStatus, headStr, self.responseText)
            # f = open('logs/test.txt','a')
            # f.write(self.responseText)
            # f.close()
            # logging.debug(self.connParam['responseData'])

            # 设置响应数据准备完成的时间
            self.connParam['waitTime'] = time.time()

            # 如果请求头不包含close,即代表开启keepalived
            if self.responseHeaders.get("Connection", "") != "close":
                self.connParam["keepalive"] = True

            # # 删掉request请求数据
            # if self.connParam.has_key('requestData'):
            #     del self.connParam['requestData']

            self.modifyEpollEvent()
        except Exception as message:
            logging.error('WebApi - startResponse  : %s' % message)
        finally:
            pass

    # 快速生成响应数据并响应
    def fastResponse(self, httpStatusCode, responseText=''):
        self.responseStatus = httpStatusCode
        self.responseHeaders["Content-Type"] = 'text/html;charset=utf-8'
        if responseText:
            self.responseText = responseText
        else:
            self.responseText = STATUS.get(httpStatusCode)

        self.__startResponse()

    # 修改epoll事件
    def modifyEpollEvent(self):
        try:
            self.__epollFd.modify(self.__clientFd, select.EPOLLET | select.EPOLLOUT)
        except Exception as message:
            logging.error('WebApi - modifyEpollEvent : %s' % message)
        finally:
            pass
