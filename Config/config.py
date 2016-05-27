# -*- coding:utf-8 -*-


# 服务器监听host
HOST = ''

# 服务器监听端口
PORT = 8888

# 允许等待连接队列的最大长度
LISTEN = 10240

# 启动进程数量,设置为0将根据cpu核心数来创建
PROCESSES_NUM = 1

# 设置单个进程启动的线程数量，线程总数 = PROCESSES_NUM * THREADS_NUM
THREADS_NUM = 1

# 设置每个进程的epoll队列数量,即最大可处理连接数为 WORKER_CONNECTIONS * PROCESSES_NUM
WORKER_CONNECTIONS = 655350

# 设置缓冲区大小
BUFFER_SIZE = 1024

# 设置缓冲区大小
RCV_BUFFER_SIZE = 16 * 1024

# 是否gzip压缩 html,css,js 图片
GZIP = False

# 设置允许压缩的页面最小字节数,建议设置成大于1k的字节数
GZIP_MIN_LENGTH = 1024

# 设置压缩级别
GZIP_LEVEL = 8

# 需要开启压缩的文件类型
GZIP_TYPES = (
'text/html', 'application/x-javascript', 'text/css', 'text/javascript', 'image/jpeg', 'image/gif', 'image/png')

# 自动去除html,css,js中的注释以及重复的空白符【\n，\r，\t，' '】 ---------  只有html, css, js才可以执行TRIM
TRIM = True

# 允许TRIM的类型
TRIM_TYPES = ('text/html', 'text/css', 'text/javascript')

# 缓存时长(秒),设置为0代表不缓存---Cache-Control: no-cache
CACHE_TIME = 10

# 当静态文件大小超过设置的值的时候,开启Transfer-Encoding : chunked;不开启的话请可以设置0
CHUNKED_MIN_LENGTH = 0

# 默认controller,例如: index，默认调用index.py。
CONTROLLER = 'index'

# 连接超时时间
TIMEOUT = 1

# keep-alive超时时间设置 --- 多少秒钟没有请求就关闭端口
KEEP_ALIVE_TIMEOUT = 3

# 开发模式下可以用，实时更新代码
AUTO_RELOAD = False

# 后台运行模式
DAEMON = False

# 日志级别 'ERROR' > 'WARNING' > 'INFO' > 'DEBUG'
LOG_LEVEL = 'INFO'

LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" ''$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" "$http_x_forwarded_for"'

# 日志过期时间——超出时间将删除
LOG_EXPIRATION_TIME = 30

CONTENT_TYPE = {
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

STATUS = {
    200: 'OK', 201: 'Created', 202: 'Accepted', 206: 'Partial Content',
    301: 'Moved Permanently', 302: 'Found', 303: 'See Other', 304: 'Not Modified', 307: 'Temporary Redirect',
    400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 405: 'Method Not Allowed',
    406: 'Not Acceptable', 409: 'Conflict', 410: 'Gone', 412: 'Precondition Failed', 415: 'Unsupported Media Type',
    500: 'InternalError', 502: 'Bad Gateway', 504: 'Gateway timeout'
}
