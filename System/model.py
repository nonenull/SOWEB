# -*- coding:utf-8 -*-

from Config import dbconfig
import pymysql
import traceback
from System.mylog import myLogging as logging


class Model:
    def __init__(self, dbName=None):
        self.conn = None
        # 初始化参数
        self.__host = dbconfig.DB_HOST
        self.__user = dbconfig.DB_USER
        self.__password = dbconfig.DB_PASSWD
        # 如果没有自定义实例化的数据库,按照配置文件中的默认数据库
        if dbconfig:
            self.__db = dbName
        else:
            self.__db = dbconfig.DB_NAME
        self.__charset = dbconfig.DB_CHARSET

        # 获取数据量连接
        self.getConn()

    '''
        获取数据库连接
    '''

    def getConn(self):
        # Connect to the database
        try:
            self.conn = pymysql.connect(host=self.__host, user=self.__user, password=self.__password, db=self.__db,
                                        charset=self.__charset, cursorclass=pymysql.cursors.DictCursor)
        except pymysql.Error as e:
            logging.error('conn', e)

    def selectOne(self):
        pass

    def select(self):
        with self.conn.cursor() as cursor:
            sql = "SELECT * FROM `bpbjj`.`users` WHERE `palayerId`=%s" % ('100000',)
            cursor.execute(sql)
            return cursor.fetchall()

    '''
        @return Boolean
        根据条件查询记录是否存在
    '''

    def find(self):
        pass

    def insert(self, table, data):
        keyList = []
        valueList = []
        # 给表名添加斜引号
        table = self.__convertTableName(table)

        if type(data) == dict:
            for k, v in data.items():
                keyList.append("`%s`" % k)
                # 将值转化为供解释器读取的形式,自带引号
                valueList.append("%s" % repr(v))
        elif type(data) == list:
            pass
        joinKey = ','.join(keyList)
        joinValue = ','.join(valueList)
        sql = 'insert into %s (%s) values (%s)' % (table, joinKey, joinValue)
        # logging.debug(sql)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
            self.conn.commit()
        except pymysql.Error as e:
            logging.error(sql, e)

    def insertMany(self, table, data):
        for i in data:
            self.insert(table, i)

    def delete(self):
        pass

    def update(self):
        pass

    '''
        @param sql SQL语句
        直接执行SQL语句
    '''

    def query(self, sql):
        pass

    '''
        @param tableName 表
        @return str
        给表名添加` 斜引号
        如果 table参数带了数据库名,比如test.user,将其转换为 `test`.`user`
    '''

    def __convertTableName(self, tableName):
        if '.' in tableName:
            convertTableName = '`%s`' % tableName.replace('.', '`.`')
        else:
            convertTableName = '`%s`' % tableName
        return convertTableName

    def __del__(self):
        try:
            print('结束了')
            self.conn.close()
        except AttributeError:
            pass


db = Model()

# if __name__ == '__main__':
#     try:
#         db = Model()
#         a = 'fuckyou'
#         db.insertMany('bpbjj.users', [{'playerid': 1, 'playerName': a},{'playerid': 2, 'playerName': a},{'playerid': 3, 'playerName': a},{'playerid': 4, 'playerName': a}])
#     except Exception as e:
#         print('+++++++++++++++++',e)
#         # db.select('a','b','c').from('table').where('d = 10 and e = 20').limit(10).order('id desc')
