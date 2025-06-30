import pymysql
from pymysql import Error

class DatabaseConnection:
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.database = 'academia'
        self.user = 'yyc'  # 修改为你的用户名
        self.password = 'C3stMySQL'  # 修改为你的密码
        
    def get_connection(self):
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            return connection
        except Error as e:
            print(f"数据库连接错误: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """执行查询语句"""
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"查询执行错误: {e}")
                return None
            finally:
                connection.close()
        return None
    
    def execute_update(self, query, params=None):
        """执行更新/插入/删除语句"""
        connection = self.get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                return cursor.rowcount
            except Error as e:
                print(f"更新执行错误: {e}")
                connection.rollback()
                return -1
            finally:
                connection.close()
        return -1