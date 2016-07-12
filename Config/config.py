# -*- coding:utf-8 -*-


# 服务器监听host
HOST = ''

# 服务器监听端口
PORT = 8888

# 允许等待连接队列的最大长度
BACKLOG = 1024

# 启动进程数量,设置为0将根据cpu核心数来创建
PROCESSES_NUM = 1

# 设置单个进程启动的线程数量，线程总数 = PROCESSES_NUM * THREADS_NUM
THREADS_NUM = 10

# 设置每个进程的epoll队列数量,即最大可处理连接数为 WORKER_CONNECTIONS * PROCESSES_NUM
WORKER_CONNECTIONS = 655350

# 设置缓冲区大小
SNT_BUFFER_SIZE = 1024

# 设置缓冲区大小
RCV_BUFFER_SIZE = 1024

# 是否gzip压缩 html,css,js 图片
GZIP = False

# 设置允许压缩的页面最小字节数,建议设置成大于1k的字节数
GZIP_MIN_LENGTH = 1024

# 设置压缩级别
GZIP_LEVEL = 8

# 需要开启压缩的文件类型
GZIP_TYPES = ('text/html', 'application/x-javascript', 'text/css', 'text/javascript', 'image/jpeg', 'image/gif', 'image/png')

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

# 是否开启keepalive
KEEP_ALIVE = False

# keep-alive超时时间设置 --- 多少秒钟没有请求就关闭端口
KEEP_ALIVE_TIMEOUT = 30

# 后台运行模式,开启了将不会在终端输出日志信息
DAEMON = False

# 日志级别 'ERROR' > 'INFO' > 'DEBUG'
LOG_LEVEL = 'DEBUG'

# 生成HTTP访问日志的格式
LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" ''$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" "$http_x_forwarded_for"'

# 日志过期时间——超出时间将删除,单位:天
LOG_EXPIRATION_TIME = 30