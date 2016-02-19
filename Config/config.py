# -*- coding:utf-8 -*-


# 服务器监听host
HOST = ''

# 服务器监听端口
PORT = 8888

# 允许等待连接队列的最大长度
LISTEN = 10240

# 启动进程数量,设置为0将根据cpu核心数来创建
PROCESSES_NUM = 0

#设置每个进程的epoll队列数量,即最大可处理连接数为 WORKER_CONNECTIONS * PROCESSES_NUM
WORKER_CONNECTIONS = 65535

# 设置单个进程启动的线程数量，线程总数 = PROCESSES_NUM * THREADS_NUM
THREADS_NUM = 20

# 每次接收多少字节的数据
BUFFER_SIZE = 1024

# 是否gzip压缩 html,css,js 图片
GZIP = True

# 需要开启压缩的文件类型
GZIP_TYPES = ('text/html', 'application/x-javascript', 'text/css', 'text/javascript', 'image/jpeg', 'image/gif', 'image/png')

# 自动去除html,css,js中的注释以及重复的空白符【\n，\r，\t，' '】 ---------  只有html, css, js才可以执行TRIM
TRIM = True

# 缓存时长(秒),设置为0代表不缓存---Cache-Control: no-cache
CACHE_TIME = 10

# 默认controller,例如: index，默认调用index.py。
CONTROLLER = 'index'

# 连接超时时间
TIMEOUT = 3

# 开发模式下可以用，实时更新代码
AUTO_RELOAD = True

# 后台运行模式
DAEMON = False

# 日志级别 'ERROR' > 'WARNING' > 'INFO' > 'DEBUG'
LOG_LEVEL = 'DEBUG'

LOG_FORMAT = '$remote_addr - $remote_user [$time_local] "$request" ''$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" "$http_x_forwarded_for"'

#日志过期时间——超出时间将删除
LOG_EXPIRATION_TIME = 30