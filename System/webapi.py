# -*- coding:utf-8 -*-

from io import StringIO
from imp import reload
from urllib.parse import parse_qs
import mimetypes
from http import HTTPStatus

import traceback

import tenjin
from tenjin.helpers import *
from tenjin.html import *

import os, sys, re, time, gzip, socket, select
from Config.config import CONTROLLER, KEEP_ALIVE, KEEP_ALIVE_TIMEOUT, CACHE_TIME, GZIP, \
    GZIP_LEVEL, \
    GZIP_MIN_LENGTH, GZIP_TYPES, TRIM, \
    TRIM_TYPES, CHUNKED_MIN_LENGTH
from System.upload import Upload,UploadCheckError
from System.mylog import myLogging as logging
from System.helper import Helper

try:
    Help = Helper()
    Help.createPath()
    Help.addSysPath()
    Help.getControllerInfo()
except Exception:
    pass

# 执行Helper类
_ctlPath = Help.ctlPath
_ctlImportDic = Help.ctlImportDic
_ctlModifyMTimeDic = Help.ctlModifyMTimeDic
_staticDirPath = Help.staticDirPath
_cacheDirPath = Help.cacheDirPath
_memoryCacheDirPath = Help.memoryCacheDirName


class WebApi:
    def __init__(self, epollFd, fd, connParam):
        logging.debug('%d - 开始解析http请求' % fd)

        # 请求头
        self.requestHeaders = {}

        # 初始化response 信息
        self.httpVersion = 'HTTP/1.1'
        self.requestUri = '/'

        # 初始化响应头
        self.responseHeaders = {}
        self.responseStatus = 200
        self.responseText = ''
        self.responseHeaders["Content-Type"] = 'text/html;charset=utf-8'
        if KEEP_ALIVE:
            self.responseHeaders["Connection"] = 'keep-alive'
            self.responseHeaders['Keep-Alive'] = 'timeout=%d' % KEEP_ALIVE_TIMEOUT
        else:
            self.responseHeaders["Connection"] = 'close'

        # 设置默认的控制器
        self.controller = CONTROLLER
        # 默认action
        self.action = 'index'

        self.getParamsDic = {}
        self.postParamsDic = {}
        self.postFileDic = {}
        self.connParam = connParam
        self.__epollFd = epollFd
        self.__clientFd = fd

        self.fuck = self.__parse
        # 开始解析 header 和 body
        # logging.debug('++++++++++++++++', connParam.get('requestData'))
        self.__parse(connParam.get('requestData'))
        logging.debug('----------------', time.time())

        # 开始准备响应工作
        # 判断请求网站图标,如果是重新生成图标位置
        if self.requestUri == "/favicon.ico":
            self.requestUri = "/" + _staticDirPath + self.requestUri

        # 判断是静态文件还是动态文件
        if _staticDirPath in self.requestUri or "favicon.ico" in self.requestUri:
            self.__handleStaticFile()
        else:
            self.__handledynamicFile()
        logging.debug('****************', time.time())

    '''
        解析请求数据
    '''

    def __parse(self, requestData):
        # 将header解析成dic存起来
        def saveResquestHeader(headerList):
            for item in headerList:
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

        # 获取控制器和动作
        def getControllerAndAction(splitRequestUri):
            # 删除所有空元素
            while '' in splitRequestUri:
                splitRequestUri.remove('')

            splitRequestUriLen = len(splitRequestUri)

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
                        self.getParamsDic[i] = param
                        i = i + 1

            elif splitRequestUriLen == 1:
                self.controller = splitRequestUri[0]
                self.action = 'index'

            else:
                self.controller = 'index'
                self.action = 'index'

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
        try:
            # 获取 header 和 body
            header, requestBody = requestData.split("\r\n\r\n", 1)
            headerList = header.split("\r\n")
            # 将header解析成dic存起来
            saveResquestHeader(headerList)
            # logging.debug('**********原始头部********',self.requestHeaders)

        except ValueError as e:
            self.fastResponse(500)
            logging.error('@@@@@@@@@@@@@@', requestData)
            return

        # 获取request 请求信息
        headerFirstLine = headerList.pop(0)
        # _logger.debug('第一行 %s'%headerFirstLine)
        # 按照空格切割 ‘GET /xxx HTTP/1.1’
        self.requestMethod, self.requestUri, self.httpVersion = re.split('\s+', headerFirstLine)

        # 将请求方法类型转为小写
        methodToLower = self.requestMethod.lower()
        # 根据?切割,有get参数的情况下 /controller/action?xxx=xxx
        splitRequestUri = self.requestUri.split('?')

        # 如果大于1,说明?后面有get参数
        if len(splitRequestUri) > 1:
            self.baseUri, self.paramStr = splitRequestUri
        else:
            self.paramStr = None
            # /controller/action
            self.baseUri = splitRequestUri[0]
            self.requestParamStr = None

        splitRequestUri = self.baseUri.split('/')
        # 获取 请求资源的文件名和 后缀(如果有的话)
        self.__fileName = splitRequestUri[-1]
        # self.__filePrefixName, self.__fileExtName = os.path.splitext(splitRequestUri[-1])

        # 截取controller和action
        getControllerAndAction(splitRequestUri)

        # 判断请求类型,保存参数
        if methodToLower == "get" and self.paramStr:
            if "?" in self.requestUri:
                # 获取?后面的的参数和值,如果有/xxx/xx/xx/xxx/xxx类型的参数,将?后面的参数合并到self.getParamsDic
                if self.getParamsDic:
                    self.getParamsDic = dict(parse_qs(self.paramStr), **self.getParamsDic)
            else:
                self.getParamsDic = parse_qs(self.paramStr)

        elif methodToLower == "post":
            # Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryZhSJu2it4yyuMdlM
            if self.requestHeaders.get('Content-Type', "").find("boundary") > 0:
                # logging.debug('++++++++++fuck 11111 you+++++++++++++++')
                self.__parseMultipartPost(requestBody)
            else:
                self.postParamsDic = parse_qs(requestBody)

    '''
        解析 Content-Type为multipart/form-data; 的requestBody
    '''
    def __parseMultipartPost(self,requestBody):
        try:
            # logging.debug('requestBody',requestBody)
            # multipart/form-data; boundary=----WebKitFormBoundaryMmTyCOdF17gBJbHF
            # 获取boundary=后面的字符串
            boundary = self.requestHeaders['Content-Type'].split('=')[-1]
            # -- 标记结束,[数据内容以两条横线结尾，并同样以一个换行结束]
            postList = requestBody.split('--'+boundary)
            # logging.debug('postList',postList)
            for i in postList:
                # 排除掉空格等
                if 'name' not in i:
                    continue

                if '\r\n\r\n' in i:
                    splitStr = '\r\n\r\n'
                else:
                    splitStr = '\n\n'

                splitItem = i.split(splitStr,maxsplit=1)
                # logging.debug('itItem',splitItem)
                describeNameStr = splitItem[0]
                describeNameDic = {}
                # 判断有上传文件的情况
                if 'Content-Type' in describeNameStr and 'filename=' in describeNameStr:
                    desItems = describeNameStr.split('\r\n')[1].split(';')
                    for desitem in desItems:
                        # logging.debug('----------------',desItems)
                        if '=' in desitem:
                            # logging.debug(desitem)
                            desSplitItem = desitem.split("=")
                            itemName = desSplitItem[0].strip()
                            # logging.debug(desSplitItem[1])
                            # 转换编码,防止中文乱码
                            itemValue = desSplitItem[1].strip().strip('"').encode('ISO-8859-1').decode('UTF-8')
                            describeNameDic[itemName] = itemValue
                            # logging.debug(describeNameDic)
                            # logging.debug(itemName,itemValue)

                    # logging.debug(describeNameDic)
                    postName = describeNameDic.get('name')
                    # logging.debug(splitItem)
                    postValue = [describeNameDic.get('filename'),splitItem[-1].strip()]
                    self.postFileDic[postName] = postValue
                    # logging.debug(self.postFileDic)
                else:
                    postName = describeNameStr.split("name=")[-1].strip('"')
                    postValue = splitItem[-1].strip()
                # logging.debug('postName=',postName,'   postValue=',postValue)
                    self.postParamsDic[postName] = postValue
            # logging.debug('+++++++++++++++++++++',self.postParamsDic)
        except Exception as e:
            logging.error(e)
            pass

    '''
        处理静态文件
    '''

    def __handleStaticFile(self):

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

            # 设置Content-Type,如果是列表中不存在的类型,按照未知获取
            contentType = mimetypes.guess_type(self.__fileName)[0]
            if contentType:
                self.responseHeaders['Content-Type'] = contentType
            else:
                self.responseHeaders['Content-Type'] = 'application/octet-stream'

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

            with open(staticFileFullPath) as staticFile:
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
            bufferSize = fileSize / 4
            beginOffset = 0
            endOffset = bufferSize
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

            # 获取格林威治(GMT)格式的文件修改时间
            fileModifyTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(fileModifyTime))

            # 获取格林威治(GMT)格式的当前时间
            currentTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))

            # 检查缓存是否到期
            isFileCacheExpiry()

            # # 后缀去掉.符号
            # extName = self.__fileExtName.replace('.', '')

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
                self.connParam['connections'].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, fileSize * 2)
                self.connParam['connections'].setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)

            # 打开文件
            with open(staticFileFullPath) as staticFile:
                # Range 只请求实体的一部分，指定范围 ---- 即断点续传
                if "Range" in self.requestHeaders:
                    rangeResponse()
                else:
                    generateResponseText()

        except OSError as e:
            self.fastResponse(404)
            logging.error(e)
            return

        except Exception as e:
            self.fastResponse(500)
            logging.error(e)
            return
        else:
            self.__startResponse()

    '''
        处理动态文件
    '''

    def __handledynamicFile(self):
        try:
            ctlFilePath = os.path.join(_ctlPath, self.controller + '.py')
            # 获取文件的最近修改时间
            mtime = os.path.getmtime(ctlFilePath)

            controller = _ctlImportDic.get(self.controller)
            # 判断突然增加controller文件的情况
            if controller == None:
                controller = __import__(self.controller)
                # 更新文件信息
                _ctlModifyMTimeDic[self.controller] = mtime
                _ctlImportDic[self.controller] = controller

            else:
                # 获取文件记录的修改时间
                lastMTime = _ctlModifyMTimeDic[self.controller]

                # 如果文件有更新
                if mtime > lastMTime:
                    controller = reload(sys.modules[self.controller])
                    _ctlModifyMTimeDic[self.controller] = mtime
                    _ctlImportDic[self.controller] = controller

            # 从导入的controller模块中获取要调用的action方法
            action = getattr(controller, self.action)

            # 获取返回值
            try:
                actionReturn = action(self)
            except Exception as e:
                self.fastResponse(500, e)
            else:
                if actionReturn:
                    self.responseText = str(actionReturn)

            # 如果配置了gzip,且大小超过设定值
            if GZIP and len(self.responseText) > GZIP_MIN_LENGTH:
                buf = StringIO()
                f = gzip.GzipFile(mode='wb', fileobj=buf, compresslevel=GZIP_LEVEL)
                f.write(self.responseText)
                f.close()
                # self.responseText = gzip.GzipFile(data=self.responseText, compresslevel=8)
            self.__startResponse()

        except ImportError as e:
            self.fastResponse(404)
            logging.error(e)

        except Exception as e:
            self.fastResponse(500)
            logging.error(e)

        finally:
            pass

    '''
        删除文件中的 注释,空格,换行符,制表符
    '''

    def trim(self, file):
        fileFd = open(file)
        try:
            data = fileFd.read()

            # 设置 匹配注释 正则表达式
            annotationReg = re.compile('(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)')

            # 设置 匹配空格,换行符,制表符 正则表达式
            spaceReg = re.compile('\s+')

            # 去掉注释
            annotationTrimData = re.sub(annotationReg, '', data)

            # 再去掉 空格,换行符,制表符
            spaceTrimData = re.sub(spaceReg, '', annotationTrimData)
            return spaceTrimData
        except Exception as e:
            logging.error(e)
        finally:
            fileFd.close()

    '''
        获取 GET 或者 POST 参数,默认两种都获取
    '''

    def input(self, method=None):
        method = method.lower()
        if method == 'get':
            return self.getParamsDic
        elif method == 'post':
            return self.postParamsDic
        elif method == 'file':
            return self.postFileDic
        else:
            inputDic = {}
            inputDic.update(self.getParamsDic)
            inputDic.update(self.postParamsDic)
            inputDic.update(self.postFileDic)
            return inputDic

    '''
        保存上传的文件
    '''
    def saveFile(self,name,config):
        try:
            fileData = self.postFileDic.get(name)
            Upload(fileData,config)
        except UploadCheckError as e:
            # 捕获自定义异常
            return e
        except Exception as e:
            traceback.print_exc()
            # logging.error(e)
            return e
        else:
            return True
    '''
        调用模板引擎生成HTML代码
    '''

    def render(self, templateName, context=None):
        if not context:
            context = {}
        renderPath = 'View/'
        try:
            engine = tenjin.Engine()
            # 文件名允许省略后缀
            if '.html' not in templateName:
                templateHtml = engine.render(renderPath + templateName + '.html', context)
            else:
                templateHtml = engine.render(renderPath + templateName, context)

            return templateHtml

        except tenjin.TemplateNotFoundError as e:
            self.fastResponse(404, 'Template Not Found')
            logging.error(e)

        except tenjin.ParseError as e:
            self.fastResponse(500, 'Template Parse Error')
            logging.error(e)

        except tenjin.TemplateSyntaxError as e:
            self.fastResponse(500, 'Template Syntax Error')
            logging.error(e)

    # 拼接Header，响应报文
    def __startResponse(self):
        try:

            # 例如 403 Forbidden
            httpStatus = "%d %s" % (self.responseStatus, HTTPStatus(self.responseStatus).phrase)
            headStr = ''

            # 获取响应内容长度
            responseTextLen = len(self.responseText.encode())

            logging.debug('=========================',self.responseText,len(self.responseText))

            # Transfer-Encoding 和 Content-Length 不可共存
            if 'Transfer-Encoding' not in self.responseHeaders:
                self.responseHeaders["Content-Length"] = responseTextLen

            self.connParam['responseTextLen'] = responseTextLen

            # 拼接Header
            for key in self.responseHeaders:
                headStr += "%s: %s\r\n" % (key, self.responseHeaders[key])

            # 拼接完整response
            self.connParam['responseData'] = "%s %s\r\n%s\n%s" % (
                self.httpVersion, httpStatus, headStr, self.responseText)

            # 设置响应数据准备完成的时间
            self.connParam['waitTime'] = time.time()

            # 如果请求头不包含close,即代表开启keepalived
            if self.responseHeaders.get("Connection", "") != "close":
                self.connParam["keepalive"] = True

            # # 删掉request请求数据
            # if self.connParam.has_key('requestData'):
            #     del self.connParam['requestData']

            self.__modifyEpollEvent()
        except Exception as e:
            logging.error('WebApi - startResponse  : %s' % e)
        finally:
            pass

    # 快速生成响应数据并响应
    def fastResponse(self, httpStatusCode, responseText=''):
        self.responseStatus = httpStatusCode
        if responseText:
            self.responseText = str(responseText)
        else:
            self.responseText = HTTPStatus(httpStatusCode).description

        self.__startResponse()

    # 修改epoll事件
    def __modifyEpollEvent(self):
        try:
            self.__epollFd.modify(self.__clientFd, select.EPOLLET | select.EPOLLOUT)
        except socket.error as e:
            # 过滤掉errno 2 和errno 9 两者出现基本都是因为 服务端准备发送数据的时候客户端已经把连接关闭掉的情况下
            if e.errno not in (2, 9):
                logging.error('WebApi - __modifyEpollEvent : %s  %d' % (e, e.errno))
        finally:
            pass
