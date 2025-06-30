# test_connection.py
import pymysql
from pymysql import Error

def test_database_connection():
    """测试数据库连接"""
    # 数据库连接配置 - 请根据你的实际情况修改
    config = {
        'host': 'localhost',
        'port': 3306,
        'database': 'academia',
        'user': 'yyc',  # 修改为你的用户名
        'password': 'C3stMySQL',  # 修改为你的密码
        'charset': 'utf8mb4'
    }
    
    try:
        print("正在尝试连接数据库...")
        print(f"主机: {config['host']}:{config['port']}")
        print(f"数据库: {config['database']}")
        print(f"用户: {config['user']}")
        print("-" * 40)
        
        # 尝试连接
        connection = pymysql.connect(**config)
        
        if connection:
            print("✅ 数据库连接成功！")
            
            # 获取数据库游标
            cursor = connection.cursor()
            
            # 测试查询 - 显示数据库版本
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL版本: {version[0]}")
            
            # 测试查询 - 显示所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 数据库中的表数量: {len(tables)}")
            print("表列表:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 测试每个表的结构和数据
            print("\n" + "="*50)
            print("表结构和数据测试:")
            print("="*50)
            
            table_names = ['Teacher', 'Course', 'Paper', 'Project', 'Teacher_Course', 'Teacher_Paper', 'Teacher_Project']
            
            for table_name in table_names:
                try:
                    print(f"\n🔍 表: {table_name}")
                    print("-" * 30)
                    
                    # 显示表结构
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    print("字段结构:")
                    for col in columns:
                        print(f"  {col[0]} - {col[1]} - {col[2]} - {col[3]}")
                    
                    # 显示数据数量
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"数据记录数: {count}")
                    
                    # 如果有数据，显示前几条
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        sample_data = cursor.fetchall()
                        print("示例数据:")
                        for i, row in enumerate(sample_data, 1):
                            print(f"  行{i}: {row}")
                    
                except Error as e:
                    print(f"❌ 表 {table_name} 测试失败: {e}")
            
            # 关闭连接
            cursor.close()
            connection.close()
            print(f"\n✅ 连接测试完成，数据库连接正常！")
            return True
            
    except Error as e:
        print(f"❌ 数据库连接失败!")
        print(f"错误信息: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查数据库服务是否启动")
        print("2. 检查用户名和密码是否正确")
        print("3. 检查主机地址和端口是否正确")
        print("4. 检查数据库名称是否存在")
        print("5. 检查用户是否有访问权限")
        return False
    
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        return False

def test_basic_operations():
    """测试基本的数据库操作"""
    config = {
        'host': 'localhost',
        'port': 3306,
        'database': 'academia',
        'user': 'yyc',  # 修改为你的用户名
        'password': 'C3stMySQL',  # 修改为你的密码
        'charset': 'utf8mb4'
    }
    
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("\n" + "="*50)
        print("测试基本数据库操作:")
        print("="*50)
        
        # 测试插入操作
        print("\n🧪 测试插入操作...")
        try:
            # 插入测试教师
            insert_teacher = """
            INSERT INTO Teacher (teacher_id, name, gender, title) 
            VALUES ('T001', '测试教师', 1, 3) 
            ON DUPLICATE KEY UPDATE name='测试教师'
            """
            cursor.execute(insert_teacher)
            connection.commit()
            print("✅ 教师数据插入成功")
            
            # 测试查询
            cursor.execute("SELECT * FROM Teacher WHERE teacher_id = 'T001'")
            result = cursor.fetchone()
            if result:
                print(f"✅ 查询成功: {result}")
            
            # 清理测试数据
            cursor.execute("DELETE FROM Teacher WHERE teacher_id = 'T001'")
            connection.commit()
            print("✅ 测试数据清理成功")
            
        except Error as e:
            print(f"❌ 操作测试失败: {e}")
        
        cursor.close()
        connection.close()
        print("✅ 基本操作测试完成")
        
    except Error as e:
        print(f"❌ 基本操作测试失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("     数据库连接测试程序")
    print("=" * 60)
    
    # 测试连接
    if test_database_connection():
        # 如果连接成功，测试基本操作
        test_basic_operations()
        
        print("\n🎉 所有测试完成!")
        print("你现在可以运行主程序了: python main.py")
    else:
        print("\n❌ 请先解决连接问题后再运行主程序")
    
    input("\n按回车键退出...")