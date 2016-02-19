# -*- coding:utf-8 -*-

from StringIO import StringIO
from urlparse import parse_qs
from Cheetah.Template import Template
import os, sys, re, cgi, time, gzip
from helper import Helper
from Config import config
import select
import log as logger

Helper = Helper()
Helper.createPath()
# 执行Helper类
_actionDic = Helper.actionDic
_actionTime = Helper.actionTime
_staticDirPath = Helper.staticDirPath
_cacheDirPath = Helper.cacheDirPath
_memoryCacheDirPath = Helper.memoryCacheDirName

_contentType = {
    '323': 'text/h323',
    'acx': 'application/internet-property-stream',
    'ai': 'application/postscript',
    'aif': 'audio/x-aiff',
    'aifc': 'audio/x-aiff',
    'aiff': 'audio/x-aiff',
    'asf': 'video/x-ms-asf',
    'asr': 'video/x-ms-asf',
    'asx': 'video/x-ms-asf',
    'au': 'audio/basic',
    'avi': 'video/x-msvideo',
    'axs': 'application/olescript',
    'bas': 'text/plain',
    'bcpio': 'application/x-bcpio',
    'bin': 'application/octet-stream',
    'bmp': 'image/bmp',
    'c': 'text/plain',
    'cat': 'application/vnd.ms-pkiseccat',
    'cdf': 'application/x-cdf',
    'cer': 'application/x-x509-ca-cert',
    'class': 'application/octet-stream',
    'clp': 'application/x-msclip',
    'cmx': 'image/x-cmx',
    'cod': 'image/cis-cod',
    'cpio': 'application/x-cpio',
    'crd': 'application/x-mscardfile',
    'crl': 'application/pkix-crl',
    'crt': 'application/x-x509-ca-cert',
    'csh': 'application/x-csh',
    'css': 'text/css',
    'dcr': 'application/x-director',
    'der': 'application/x-x509-ca-cert',
    'dir': 'application/x-director',
    'dll': 'application/x-msdownload',
    'dms': 'application/octet-stream',
    'doc': 'application/msword',
    'dot': 'application/msword',
    'dvi': 'application/x-dvi',
    'dxr': 'application/x-director',
    'eps': 'application/postscript',
    'etx': 'text/x-setext',
    'evy': 'application/envoy',
    'exe': 'application/octet-stream',
    'fif': 'application/fractals',
    'flr': 'x-world/x-vrml',
    'gif': 'image/gif',
    'gtar': 'application/x-gtar',
    'gz': 'application/x-gzip',
    'h': 'text/plain',
    'hdf': 'application/x-hdf',
    'hlp': 'application/winhlp',
    'hqx': 'application/mac-binhex40',
    'hta': 'application/hta',
    'htc': 'text/x-component',
    'htm': 'text/html',
    'html': 'text/html',
    'htt': 'text/webviewhtml',
    'ico': 'image/x-icon',
    'ief': 'image/ief',
    'iii': 'application/x-iphone',
    'ins': 'application/x-internet-signup',
    'isp': 'application/x-internet-signup',
    'jfif': 'image/pipeg',
    'jpe': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'js': 'application/x-javascript',
    'latex': 'application/x-latex',
    'lha': 'application/octet-stream',
    'lsf': 'video/x-la-asf',
    'lsx': 'video/x-la-asf',
    'lzh': 'application/octet-stream',
    'm13': 'application/x-msmediaview',
    'm14': 'application/x-msmediaview',
    'm3u': 'audio/x-mpegurl',
    'man': 'application/x-troff-man',
    'mdb': 'application/x-msaccess',
    'me': 'application/x-troff-me',
    'mht': 'message/rfc822',
    'mhtml': 'message/rfc822',
    'mid': 'audio/mid',
    'mny': 'application/x-msmoney',
    'mov': 'video/quicktime',
    'movie': 'video/x-sgi-movie',
    'mp2': 'video/mpeg',
    'mp3': 'audio/mpeg',
    'mpa': 'video/mpeg',
    'mpe': 'video/mpeg',
    'mpeg': 'video/mpeg',
    'mpg': 'video/mpeg',
    'mpp': 'application/vnd.ms-project',
    'mpv2': 'video/mpeg',
    'ms': 'application/x-troff-ms',
    'mvb': 'application/x-msmediaview',
    'nws': 'message/rfc822',
    'oda': 'application/oda',
    'p10': 'application/pkcs10',
    'p12': 'application/x-pkcs12',
    'p7b': 'application/x-pkcs7-certificates',
    'p7c': 'application/x-pkcs7-mime',
    'p7m': 'application/x-pkcs7-signature',
    'p7r': 'application/x-pkcs7-certreqresp',
    'p7s': 'application/x-pkcs7-signature',
    'pbm': 'image/x-portable-bitmap',
    'pdf': 'application/x-pkcs12',
    'pfx': 'application/x-pkcs12',
    'pgm': 'image/x-portable-graymap',
    'pko': 'application/ynd.ms-pkipko',
    'pma': 'application/x-perfmon',
    'pmc': 'application/x-perfmon',
    'pml': 'application/x-perfmon',
    'pmr': 'application/x-perfmon',
    'pmw': 'application/x-perfmon',
    'pnm': 'image/x-portable-anymap',
    'pot': 'application/vnd.ms-powerpoint',
    'ppm': 'image/x-portable-pixmap',
    'pps': 'application/vnd.ms-powerpoint',
    'ppt': 'application/vnd.ms-powerpoint',
    'prf': 'application/pics-rules',
    'ps': 'application/postscript',
    'pub': 'application/x-mspublisher',
    'qt': 'video/quicktime',
    'ra': 'audio/x-pn-realaudio',
    'ram': 'audio/x-pn-realaudio',
    'ras': 'image/x-cmu-raster',
    'rgb': 'image/x-rgb',
    'rmi': 'audio/mid',
    'roff': 'application/x-troff',
    'rtf': 'application/rtf',
    'rtx': 'text/richtext',
    'scd': 'application/x-msschedule',
    'sct': 'text/scriptlet',
    'setpay': 'application/set-payment-initiation',
    'setreg': 'application/set-registration-initiation',
    'sh': 'application/x-sh',
    'shar': 'application/x-shar',
    'sit': 'application/x-stuffit',
    'snd': 'audio/basic',
    'spc': 'application/x-pkcs7-certificates',
    'spl': 'application/futuresplash',
    'src': 'application/x-wais-source',
    'sst': 'application/vnd.ms-pkicertstore',
    'stl': 'application/vnd.ms-pkistl',
    'stm': 'text/html',
    'svg': 'image/svg+xml',
    'sv4cpio': 'application/x-sv4cpio',
    'sv4crc': 'application/x-sv4crc',
    'swf': 'application/x-shockwave-flash',
    't': 'application/x-troff',
    'tar': 'application/x-tar',
    'tcl': 'application/x-tcl',
    'tex': 'application/x-tex',
    'texi': 'application/x-texinfo',
    'texinfo': 'application/x-texinfo',
    'tgz': 'application/x-compressed',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'tr': 'application/x-troff',
    'trm': 'application/x-msterminal',
    'tsv': 'text/tab-separated-values',
    'txt': 'text/plain',
    'uls': 'text/iuls',
    'ustar': 'application/x-ustar',
    'vcf': 'text/x-vcard',
    'vrml': 'x-world/x-vrml',
    'wav': 'audio/x-wav',
    'wcm': 'application/vnd.ms-works',
    'wdb': 'application/vnd.ms-works',
    'wks': 'application/vnd.ms-works',
    'wmf': 'application/x-msmetafile',
    'wps': 'application/vnd.ms-works',
    'wri': 'application/x-mswrite',
    'wrl': 'x-world/x-vrml',
    'wrz': 'x-world/x-vrml',
    'xaf': 'x-world/x-vrml',
    'xbm': 'image/x-xbitmap',
    'xla': 'application/vnd.ms-excel',
    'xlc': 'application/vnd.ms-excel',
    'xlm': 'application/vnd.ms-excel',
    'xls': 'application/vnd.ms-excel',
    'xlt': 'application/vnd.ms-excel',
    'xlw': 'application/vnd.ms-excel',
    'xof': 'x-world/x-vrml',
    'xpm': 'image/x-xpixmap',
    'xwd': 'image/x-xwindowdump',
    'z': 'application/x-compress',
    'zip': 'application/zip'
}

_responseStatusDic = {
    200: 'OK', 201: 'Created', 202: 'Accepted', 206: 'Partial Content',
    301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 307: 'Temporary Redirect',
    400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed',
    406: 'Not Acceptable', 409: 'Conflict', 410: 'Gone', 412: 'Precondition Failed', 415: 'Unsupported Media Type',
    500: 'InternalError'
}


class WebApi(object):
    def __init__(self):
        # 初始化response

        self.httpVersion = 'HTTP/1.1'

        self.requestUri = '/'
        self.controller = config.CONTROLLER

        # 请求头
        self.requestHeaders = {}

        # 预设响应头
        self.responseHeaders = {}
        self.responseStatus = 200
        self.responseText = ''
        self.responseHeaders["Content-Type"] = "text/html;charset=utf-8"
        self.responseHeaders["Connection"] = "keep-alive"

        self.action = 'index'
        self.getDic = {}
        self.form = None
        self.postDic = {}
        self.data = {}

    def parsing(self, requestData):
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
        headend = requestData.find("\r\n\r\n")
        rfile = ""
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

        # /controller/action?xxx=xxx
        splitRequestUri = self.requestUri.split('?')
        # print splitRequestUri
        if len(splitRequestUri) > 1:
            self.baseUri, self.paramStr = splitRequestUri
        else:
            self.baseUri = splitRequestUri[0]
            self.requestParamStr = None

        splitRequestUri = self.baseUri.split('/')
        self.__filePrefixName, self.__fileExtName = os.path.splitext(splitRequestUri[-1])
        # print(splitRequestUri)
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
            # 获取GET 的参数和值
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
        # 有controller和action或者GET param的情况
        if splitRequestUriLen >= 2:
            # 获取controller和action，并删除，剩下的就是GET参数
            self.controller = splitRequestUri.pop(0)
            self.action = splitRequestUri.pop(0)
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

    # gzip压缩文件,如果文件是
    def gzipAndTrim(self):
        def gzipFile():
            pass

        def trimFile():
            pass

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

    # 拼接Header，响应报文
    def __startResponse(self):
        try:
            # 例如 403 Forbidden
            httpStatus = "%d %s" % (self.responseStatus, _responseStatusDic.get(self.responseStatus))
            headStr = ''

            # 获取响应内容长度
            responseTextLen = len(self.responseText)
            self.responseHeaders["Content-Length"] = responseTextLen
            self.data['responseTextLen'] = responseTextLen

            # 拼接Header
            for key in self.responseHeaders:
                headStr += "%s: %s\r\n" % (key, self.responseHeaders[key])
            self.data["responseData"] = "%s %s\r\n%s\r\n%s" % (self.httpVersion, httpStatus, headStr, self.responseText)

            del self.data["requestData"]
            self._epollFd.modify(self._fd,select.EPOLLET | select.EPOLLOUT)

        except Exception as e:
            logger.error(e)
            pass

    def __sendResponseFile(self):

        # 判断静态文件是否存在
        def isStaticFileExist():
            if not os.path.exists(staticFileFullPath):
                self.responseText = "resource file does not exist"
                self.responseStatus = 404
                return False

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
                return False

        # 初始化部分Header
        def initHeader():
            self.responseHeaders['Last-Modified'] = fileModifyTimeStr
            self.responseHeaders['ETag'] = fileModifyTime
            self.responseHeaders['Date'] = currentTimeStr
            # 设置Content-Type
            self.responseHeaders['Content-Type'] = _contentType.get(extName)

            # 根据配置设置缓存时间
            if config.CACHE_TIME == 0:
                self.responseHeaders['Cache-Control'] = 'no-cache'
            else:
                self.responseHeaders['Cache-Control'] = 'max-age=%d' % config.CACHE_TIME

        def isNeedTrim():
            # 如果配置了TRIM,自动去除html,css,js中的注释以及重复的空白符（\n，\r，\t，' '）,否则直接读取静态文件
            if config.TRIM and extName in ['css', 'html', 'js']:
                if not os.path.exists(self.__trimFileFullPath) or os.path.getmtime(
                        self.__trimFileFullPath) < fileModifyTime:
                    trimFileData = Helper.trimFile(staticFileFullPath)
                    trimFileFd = open(self.__trimFileFullPath, 'w')
                    trimFileFd.write(trimFileData)
                    trimFileFd.close()

        # 判断是否需要gzip压缩
        def isNeedGzip():
            # 开启Gzip
            if self.responseHeaders.get('Content-Type') in config.GZIP_TYPES and config.GZIP:
                if not os.path.exists(self.__gzipFileFullPath) or os.path.getmtime(
                        self.__gzipFileFullPath) < fileModifyTime:
                    if config.TRIM:
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

        # 逻辑开始
        try:
            staticFile = None
            # 获取静态文件路径
            staticFileFullPath = self.baseUri[self.baseUri.find(_staticDirPath) + 0:]

            # 获取缓存文件路径
            cacheFileFullPath = _memoryCacheDirPath + staticFileFullPath[7:]

            isCacheDirExist()

            self.__trimFileFullPath = cacheFileFullPath + '-trim'
            self.__gzipFileFullPath = cacheFileFullPath + '-gzip'

            if isStaticFileExist() == False:
                return

            # 过期时间
            lastTimeStr = self.requestHeaders.get("If-Modified-Since", None)

            # 获取文件修改时间
            fileModifyTime = os.path.getmtime(staticFileFullPath)

            # 把文件修改时间转换为格林威治(GMT)时间
            fileModifyTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(fileModifyTime))

            # 把当前时间转换为格林威治(GMT)时间
            currentTimeStr = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))

            # 检查缓存是否到期
            if isFileCacheExpiry() == False:
                return

            # 后缀去掉.符号
            extName = self.__fileExtName.replace('.', '')

            # 初始化部分Header
            initHeader()

            # 判断是否需要缓存trim文件
            isNeedTrim()

            # 判断是否需要缓存gzip文件
            isNeedGzip()

            if config.GZIP:
                staticFileFullPath = self.__gzipFileFullPath
                self.responseHeaders['Content-Encoding'] = 'gzip'
            elif config.TRIM:
                staticFileFullPath = self.__trimFileFullPath

            # 获取文件大小
            fileSize = os.path.getsize(staticFileFullPath)

            # Range 只请求实体的一部分，指定范围 ---- 即断点续传
            if "Range" in self.requestHeaders:
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
            else:
                rangeStart = 0
                rangeEnd = fileSize - 1

            # 偏移量
            offset = rangeStart

            # 请求的分段数据总长度
            partLen = rangeEnd - rangeStart + 1
            # logger.debug('长度 %d' % partLen)

            if partLen < 0:
                partLen = 0

            self.responseHeaders['Content-Length'] = partLen

            staticFile = open(staticFileFullPath)

            # 设置文件的当前位置偏移,从偏移量开始读取数据
            staticFile.seek(offset)
            readlen = 102400
            if readlen > partLen:
                readlen = partLen

            firstdata = staticFile.read(readlen)
            self.responseText += firstdata
            partLen -= len(firstdata)

        except Exception as e:
            logger.error(str(e) + Helper.getTraceStackMsg())
            self.responseStatus = 500
            self.responseText = "load resource file fail"
            pass

        finally:
            self.__startResponse()
            if staticFile:
                staticFile.close()

    # 处理
    def process(self, data, epollFd, fd):
        self.data = data
        self._epollFd = epollFd
        self._fd = fd
        try:
            # _logger.debug('request总数据 %s' % data['requestData'])
            self.parsing(data['requestData'])

        except Exception as e:

            self.responseStatus = 500
            self.responseText = "Initializes the request failed"
            logger.error(str(e) + Helper.getTraceStackMsg())

        try:

            if self.requestUri == "/favicon.ico":
                self.requestUri = "/" + _staticDirPath + self.requestUri

            # 判断是否静态文件，判断URI是否含有Cache，Static或者favicon.ico
            if _staticDirPath in self.requestUri or "favicon.ico" in self.requestUri:
                self.__sendResponseFile()
                return None

            controller = _actionDic.get(self.controller, None)

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

            # 如果配置了gzip
            if config.GZIP and len(self.responseText) > 1024:
                self.responseText = Helper.responseGzip(self.responseText)

        except Exception as e:
            logger.error(str(e) + Helper.getTraceStackMsg())
            self.responseStatus = 500
            self.responseText = "Internal Error"

        try:
            if self.responseHeaders.get("Connection", "") != "close":
                data["keepalive"] = True

            self.__startResponse()

        except Exception as e:
            logger.error(str(e) + Helper.getTraceStackMsg())
