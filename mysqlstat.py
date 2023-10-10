import sys
import pymysql
import time
import re
from decimal import Decimal
from datetime import datetime
from prettytable import PrettyTable
import textwrap
import signal
import argparse

def mysql_status_monitor(mysql_ip:str, mysql_port:int, mysql_user:str, mysql_password:str):
    """
    mysql状态监控工具，监控mysql服务器的QPS、TPS、网络带宽等指标。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
    Returns:
        None
    """

    # 创建表格对象
    table = PrettyTable()
    table.field_names = ["Time", "Select", "Insert", "Update", "Delete", "Conn", "Max_conn", "Recv", "Send"]

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    def signal_handler(sig, frame):
        print('程序被终止')
        sys.exit(0)

    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTSTP, signal_handler)  # Ctrl+Z


    # 创建游标对象
    cursor = conn.cursor()

    # 获取数据库的初始统计信息
    cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_select'")
    prev_select_count = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_insert'")
    prev_insert_count = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_update'")
    prev_update_count = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_delete'")
    prev_delete_count = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL VARIABLES LIKE 'max_connections'")
    max_conn = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Bytes_received'")
    prev_recv = cursor.fetchone()[1]

    cursor.execute("SHOW GLOBAL STATUS LIKE 'Bytes_sent'")
    prev_send = cursor.fetchone()[1]

    # 等待1秒
    time.sleep(1)

    count = 0

    while True:
        # 执行SQL查询语句获取最新的统计数据
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_select'")
        select_count = cursor.fetchone()[1]

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_insert'")
        insert_count = cursor.fetchone()[1]

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_update'")
        update_count = cursor.fetchone()[1]

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Com_delete'")
        delete_count = cursor.fetchone()[1]

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Threads_connected'")
        conn_count = cursor.fetchone()[1]

        # 执行SQL查询语句获取最新的网络数据量统计
        cursor.execute("SHOW GLOBAL STATUS LIKE 'Bytes_received'")
        recv_bytes = cursor.fetchone()[1]

        cursor.execute("SHOW GLOBAL STATUS LIKE 'Bytes_sent'")
        send_bytes = cursor.fetchone()[1]

        # 计算每秒操作量和网络数据量
        select_per_second = int(select_count) - int(prev_select_count)
        insert_per_second = int(insert_count) - int(prev_insert_count)
        update_per_second = int(update_count) - int(prev_update_count)
        delete_per_second = int(delete_count) - int(prev_delete_count)
        recv_per_second = int(recv_bytes) - int(prev_recv)
        send_per_second = int(send_bytes) - int(prev_send)

        # 将每秒接收和发送数据量从字节转换为兆比特
        recv_mbps = recv_per_second * 8 / 1000000
        send_mbps = send_per_second * 8 / 1000000

        # 更新时间
        current_time = datetime.now()
        current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 更新统计变量
        prev_select_count = select_count
        prev_insert_count = insert_count
        prev_update_count = update_count
        prev_delete_count = delete_count
        prev_recv = recv_bytes
        prev_send = send_bytes

        # 添加数据到表格中
        table.add_row([current_time, select_per_second, insert_per_second, update_per_second, delete_per_second,
                       conn_count, max_conn, "{:.2f}".format(recv_mbps) + " MBit/s", "{:.2f}".format(send_mbps) + " MBit/s"])

        # 清空控制台
        print("\033c", end="")

        # 输出表格
        print(table)

        count += 1
        if count % 25 == 0:
            print(table)
            table.clear_rows()

        time.sleep(1)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def show_frequently_sql(mysql_ip:str, mysql_port:int, mysql_user:str, mysql_password:str, top:int):
    """
    mysql状态监控工具，统计执行次数最频繁的前N条SQL语句。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
        db_name: str, 数据库名称
        top_frequently_sql: str, 执行次数最频繁的前N条SQL语句
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 获取数据库的初始统计信息
    cursor.execute("SELECT @@performance_schema")
    is_performance_schema = cursor.fetchone()

    if is_performance_schema == 0:
        print("performance_schema参数未开启。")
        print("在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。")
        sys.exit(0)
    else:
        cursor.execute("SET @sys.statement_truncate_len = 1024")
        cursor.execute(f"select query,db,last_seen,exec_count,max_latency,avg_latency from sys.statement_analysis order by exec_count desc, last_seen desc limit {top}")
        top_info = cursor.fetchall()

        # 创建表格对象
        table = PrettyTable()
        table.field_names = ["执行语句", "数据库名", "最近执行时间", "SQL执行总次数", "最大执行时间", "平均执行时间"]

        # 设置每列的对齐方式为左对齐
        table.align = "l"
        
        for row in top_info:
            query = row[0]
            db = row[1]
            last_seen = row[2]
            exec_count = row[3]
            max_latency = row[4]
            avg_latency = row[5]

            # 处理自动换行
            wrapped_query = '\n'.join(textwrap.wrap(query, width=70))

            # 添加数据到表格中
            #table.add_row([query, db, last_seen, exec_count, max_latency, avg_latency])
            table.add_row([wrapped_query, db, last_seen, exec_count, max_latency, avg_latency])

        # 输出表格
        print(table)

        # 关闭游标和连接
        cursor.close()
        conn.close()


def show_frequently_io(mysql_ip:str, mysql_port:int, mysql_user:str, mysql_password:str, io:int):
    """
    mysql状态监控工具，统计访问次数最频繁的前N个表文件ibd。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
        top_frequently_io: str, 访问次数最频繁的前N个表文件ibd
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 获取数据库的初始统计信息
    cursor.execute("SELECT @@performance_schema")
    is_performance_schema = cursor.fetchone()

    if is_performance_schema == 0:
        print("performance_schema参数未开启。")
        print("在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。")
        sys.exit(0)
    else:
        cursor.execute("SET @sys.statement_truncate_len = 1024")
        cursor.execute(f"select file,count_read,total_read,count_write,total_written,total from sys.io_global_by_file_by_bytes limit {io}")
        top_info = cursor.fetchall()

        # 创建表格对象
        table = PrettyTable()
        table.field_names = ["表文件名", "总共读取次数", "总共读取数据量", "总共写入次数", "总共写入数据量", "总共读写数据量"]

        # 设置每列的对齐方式为左对齐
        table.align = "l"

        for row in top_info:
            file = row[0]
            count_read = row[1]
            total_read = row[2]
            count_write = row[3]
            total_written = row[4]
            total = row[5]

            # 处理自动换行
            wrapped_query = '\n'.join(textwrap.wrap(file, width=70))

            # 添加数据到表格中
            table.add_row([wrapped_query, count_read, total_read, count_write, total_written, total])

            # 添加数据到表格中
            #table.add_row([file, count_read, total_read, count_write, total_written, total])

        # 输出表格
        print(table)

        # 关闭游标和连接
        cursor.close()
        conn.close()


def show_lock_sql(mysql_ip: str, mysql_port: int, mysql_user: str, mysql_password: str):
    """
    mysql状态监控工具，查看当前锁阻塞的SQL。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
        db_name: str, 数据库名称
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    cursor.execute(
                """
                SELECT 
                    a.trx_id AS trx_id, 
                    a.trx_state AS trx_state, 
                    a.trx_started AS trx_started, 
                    b.id AS processlist_id, 
                    b.info AS info, 
                    b.user AS user, 
                    b.host AS host, 
                    b.db AS db, 
                    b.command AS command, 
                    b.state AS state, 
                    CONCAT('KILL QUERY ', b.id) AS sql_kill_blocking_query
                FROM 
                    information_schema.INNODB_TRX a, 
                    information_schema.PROCESSLIST b 
                WHERE 
                    a.trx_mysql_thread_id = b.id
                ORDER BY 
                    a.trx_started
                """
    )
    lock_info = cursor.fetchall()

    # 创建表格对象
    table = PrettyTable()
    table.field_names = ["事务ID", "事务状态", "执行时间", "processlist线程ID", "info", "user", "host", "db", "command", "state", "kill阻塞查询ID"]

    # 设置每列的对齐方式为左对齐
    table.align = "l"

    for row in lock_info:
        trx_id = row[0]
        trx_state = row[1]
        trx_started = row[2]
        processlist_id = row[3]
        info = row[4]
        user = row[5]
        host = row[6]
        db = row[7]
        command = row[8]
        state = row[9]
        sql_kill_blocking_query = row[10]

        # 处理自动换行
        #wrapped_query = '\n'.join(textwrap.wrap(query, width=70))

        # 添加数据到表格中
        table.add_row([trx_id,trx_state,trx_started,processlist_id,info,user,host,db,command,state,sql_kill_blocking_query])
        #table.add_row([wrapped_query, db, last_seen, exec_count, max_latency, avg_latency])

    # 输出表格
    print(table)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def show_redundant_indexes(mysql_ip: str, mysql_port: int, mysql_user: str, mysql_password: str):
    """
    mysql状态监控工具，查看重复或冗余的索引。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 获取数据库的初始统计信息
    cursor.execute("SELECT @@performance_schema")
    is_performance_schema = cursor.fetchone()

    if is_performance_schema == 0:
        print("performance_schema参数未开启。")
        print("在my.cnf配置文件里添加performance_schema=1，并重启mysqld进程生效。")
        sys.exit(0)
    else:
        cursor.execute("SET @sys.statement_truncate_len = 1024")
        cursor.execute("select table_schema,table_name,redundant_index_name,redundant_index_columns,sql_drop_index from sys.schema_redundant_indexes")
        redundant_info = cursor.fetchall()

        # 创建表格对象
        table = PrettyTable()
        table.field_names = ["数据库名", "表名", "冗余索引名", "冗余索引列名", "删除冗余索引SQL"]

        # 设置每列的对齐方式为左对齐
        table.align = "l"

        for row in redundant_info:
            table_schema = row[0]
            table_name = row[1]
            redundant_index_name = row[2]
            redundant_index_columns = row[3]
            sql_drop_index = row[4]

            # 处理自动换行
            # wrapped_query = '\n'.join(textwrap.wrap(query, width=70))

            # 添加数据到表格中
            table.add_row([table_schema,table_name,redundant_index_name,redundant_index_columns,sql_drop_index])
            #table.add_row([wrapped_query, db, last_seen, exec_count, max_latency, avg_latency])

        # 输出表格
        print(table)

        # 关闭游标和连接
        cursor.close()
        conn.close()


def show_conn_count(mysql_ip: str, mysql_port: int, mysql_user: str, mysql_password: str):
    """
    mysql状态监控工具，查看应用端IP连接数总和。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    cursor.execute("SELECT user,db,substring_index(HOST,':',1) AS Client_IP,count(1) AS count FROM information_schema.PROCESSLIST "
                   "GROUP BY user,db,substring_index(HOST,':',1) ORDER BY COUNT(1) DESC")
    conn_info = cursor.fetchall()

    # 创建表格对象
    table = PrettyTable()
    table.field_names = ["连接用户", "数据库名", "应用端IP", "数量"]

    # 设置每列的对齐方式为左对齐
    table.align = "l"

    for row in conn_info:
        user = row[0]
        db = row[1]
        Client_IP = row[2]
        count = row[3]

        # 添加数据到表格中
        table.add_row([user,db,Client_IP,count])

    # 输出表格
    print(table)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def show_table_info(mysql_ip: str, mysql_port: int, mysql_user: str, mysql_password: str):
    """
    mysql状态监控工具，统计库里每个表的大小。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    cursor.execute("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))")
    cursor.execute(
                    """
                    SELECT t.TABLE_SCHEMA as TABLE_SCHEMA,t.TABLE_NAME as TABLE_NAME,t.ENGINE as ENGINE,t.DATA_LENGTH/1024/1024/1024 as DATA_LENGTH,
                    t.INDEX_LENGTH/1024/1024/1024 as INDEX_LENGTH,SUM(t.DATA_LENGTH+t.INDEX_LENGTH)/1024/1024/1024 AS TOTAL_LENGTH,
                    c.column_name AS COLUMN_NAME,c.data_type AS DATA_TYPE,c.COLUMN_TYPE AS COLUMN_TYPE,t.AUTO_INCREMENT AS AUTO_INCREMENT,
                    locate('unsigned',c.COLUMN_TYPE) = 0 AS IS_SIGNED 
                    FROM information_schema.TABLES t JOIN
                    (
                    SELECT * FROM information_schema.COLUMNS WHERE extra='auto_increment'
                    ) c ON t.table_name=c.table_name 
                    WHERE t.TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys') 
                    GROUP BY TABLE_NAME 
                    ORDER BY TOTAL_LENGTH DESC,AUTO_INCREMENT DESC
                    """
    )
    conn_info = cursor.fetchall()

    # 创建表格对象
    table = PrettyTable()
    table.field_names = ["库名", "表名", "存储引擎", "数据大小(GB)", "索引大小(GB)", "总计(GB)", "主键自增字段", "主键字段属性", "主键自增当前值", "主键自增值剩余"]

    # 设置每列的对齐方式为左对齐
    table.align = "l"

    RESIDUAL_AUTO_INCREMENT = 0

    for row in conn_info:
        TABLE_SCHEMA = row[0]
        TABLE_NAME = row[1]
        ENGINE = row[2]
        DATA_LENGTH = round(row[3],2)
        INDEX_LENGTH = round(row[4],2)
        TOTAL_LENGTH = round(row[5],2)
        COLUMN_NAME = row[6]
        DATA_TYPE = row[7]
        COLUMN_TYPE = row[8]
        AUTO_INCREMENT = row[9]
        IS_SIGNED = row[10]

        if DATA_TYPE == 'int':
            if IS_SIGNED == 0:
                RESIDUAL_AUTO_INCREMENT = int(4294967295 - AUTO_INCREMENT)
            if IS_SIGNED == 1:
                RESIDUAL_AUTO_INCREMENT = int(2147483647 - AUTO_INCREMENT)

        if DATA_TYPE == 'bigint':
            if IS_SIGNED == 0:
                RESIDUAL_AUTO_INCREMENT = Decimal("18446744073709551615") - Decimal(AUTO_INCREMENT)
            if IS_SIGNED == 1:
                RESIDUAL_AUTO_INCREMENT = Decimal("9223372036854775807") - Decimal(AUTO_INCREMENT)

        # 处理自动换行
        wrapped_TABLE_NAME = '\n'.join(textwrap.wrap(TABLE_NAME, width=20))
        wrapped_COLUMN_TYPE = '\n'.join(textwrap.wrap(COLUMN_TYPE, width=10))
        wrapped_AUTO_INCREMENT = '\n'.join(textwrap.wrap(str(AUTO_INCREMENT), width=20))
        wrapped_RESIDUAL_AUTO_INCREMENT = '\n'.join(textwrap.wrap(str(RESIDUAL_AUTO_INCREMENT), width=20))

        # 添加数据到表格中
        table.add_row([TABLE_SCHEMA,wrapped_TABLE_NAME,ENGINE,DATA_LENGTH,INDEX_LENGTH,TOTAL_LENGTH,
                       COLUMN_NAME,wrapped_COLUMN_TYPE,wrapped_AUTO_INCREMENT,wrapped_RESIDUAL_AUTO_INCREMENT])

    # 输出表格
    print(table)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def show_deadlock_info(mysql_ip: str, mysql_port: int, mysql_user: str, mysql_password: str):
    """
    mysql状态监控工具，查看死锁信息。
    Args:
        mysql_ip: str, MySQL服务器IP地址
        mysql_port: int, MySQL服务器端口号
        mysql_user: str, MySQL用户名
        mysql_password: str, MySQL用户密码
    Returns:
        None
    """

    # 连接MySQL数据库
    conn = pymysql.connect(
        host=mysql_ip,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 获取死锁信息
    cursor.execute("SHOW ENGINE INNODB STATUS")
    rows = cursor.fetchall()
    innodb_status = rows[0][2]

    deadlock_info = re.search(r"LATEST DETECTED DEADLOCK.*?WE ROLL BACK TRANSACTION\s+\(\d+\)", 
                              innodb_status, re.DOTALL)
    if deadlock_info:
        print("------------------------")
        print(deadlock_info.group(0))
        print("------------------------")

    # 关闭数据库连接
    cursor.close()
    conn.close()


if __name__ == "__main__":
    # 创建ArgumentParser对象
    parser = argparse.ArgumentParser(description='MySQL命令行监控工具 - mysqlstat')

    # 添加命令行参数
    parser.add_argument('-H', '--mysql_ip', type=str, help='Mysql IP', required=True)
    parser.add_argument('-P', '--mysql_port', type=int, help='Mysql Port', required=True)
    parser.add_argument('-u', '--mysql_user', type=str, help='Mysql User', required=True)
    parser.add_argument('-p', '--mysql_password', type=str, help='Mysql Password', required=True)
    #parser.add_argument('-d', '--db_name', type=str, help='Database Name', required=True)
    parser.add_argument('--top', type=int, metavar='N', help="需要提供一个整数类型的参数值，该参数值表示执行次数最频繁的前N条SQL语句")
    parser.add_argument('--io', type=int, metavar='N', help="需要提供一个整数类型的参数值，该参数值表示访问次数最频繁的前N张表文件ibd")
    parser.add_argument('--lock', action='store_true', help="查看当前锁阻塞的SQL")
    parser.add_argument('--index', action='store_true', help="查看重复或冗余的索引")
    parser.add_argument('--conn', action='store_true', help="查看应用端IP连接数总和")
    parser.add_argument('--tinfo', action='store_true', help="统计库里每个表的大小")
    parser.add_argument('--dead', action='store_true', help="查看死锁信息")
    parser.add_argument('-v', '--version', action='version', version='mysqlstat工具版本号: 1.0.1，更新日期：2023-10-10')

    # 解析命令行参数
    args = parser.parse_args()

    # 获取变量值
    mysql_ip = args.mysql_ip
    mysql_port = args.mysql_port
    mysql_user = args.mysql_user
    mysql_password = args.mysql_password
    #db_name = args.db_name
    top_frequently_sql = args.top
    top_frequently_io = args.io
    top_lock_sql = args.lock
    top_index_sql = args.index
    top_conn_sql = args.conn
    top_table_info = args.tinfo
    top_deadlock = args.dead

    if top_frequently_sql:
        show_frequently_sql(mysql_ip, mysql_port, mysql_user, mysql_password, top_frequently_sql)
    if top_frequently_io:
        show_frequently_io(mysql_ip, mysql_port, mysql_user, mysql_password, top_frequently_io)
    if top_lock_sql:
        show_lock_sql(mysql_ip, mysql_port, mysql_user, mysql_password)
    if top_index_sql:
        show_redundant_indexes(mysql_ip, mysql_port, mysql_user, mysql_password)
    if top_conn_sql:
        show_conn_count(mysql_ip, mysql_port, mysql_user, mysql_password)
    if top_table_info:
        show_table_info(mysql_ip, mysql_port, mysql_user, mysql_password)
    if top_deadlock:
        show_deadlock_info(mysql_ip, mysql_port, mysql_user, mysql_password)
    if not top_frequently_sql and not top_frequently_io and not top_lock_sql and not top_index_sql \
        and not top_conn_sql and not top_table_info and not top_deadlock:
        mysql_status_monitor(mysql_ip, mysql_port, mysql_user, mysql_password)
