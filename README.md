# MySQL命令行监控工具 - mysqlstat 介绍

https://www.oschina.net/p/mysqlstat
#### mysqlstat 是一个命令行工具，用于实时监控和分析 MySQL 服务器的性能指标和相关信息。
#### 它可以帮助 DBA（数据库管理员）和开发人员定位和解决数据库性能问题。

```
mysqlstat工具版本号: 1.0.14，更新日期：2024-02-16 - 新增“查看当前未提交事务的SQL”
最新版下载地址：https://github.com/hcymysql/mysqlstat/releases/tag/mysqlstat_v1.0.14

当一个事务长时间未提交，那么这个连接就不能关闭，内存就不释放。如果并发一大，导致数据库连接数增多，就会对性能产生影响。

例如执行一条SQL：
begin;
update t1 set name='张三' where uid=101;
注：由于这里一直没有commit，该表就会一直持有MDL锁和行锁。
```

新版本通过指定参数--uncommit即可获取到未提交的事务SQL，如果想将其kill掉，再指定--kill即可。
<img width="895" alt="6ba49a150c13ceead2c599332ce933c" src="https://github.com/hcymysql/mysqlstat/assets/19261879/cf69e058-2e4d-4f7e-bc78-a225c628731e">


#### 以下是 mysqlstat 工具的主要功能：

mysqlstat is a command-line tool designed for real-time monitoring and analysis of performance metrics and related information of MySQL servers. 

It assists DBAs (Database Administrators) and developers in identifying and resolving database performance issues. 

The main functionalities of the mysqlstat tool are as follows: 

---------------------------------------------
* 实时监控：mysqlstat 可以实时监控 MySQL 服务器的 QPS（每秒查询数）、TPS（每秒事务数）以及网络带宽使用情况等指标。
* 查询分析：它可以展示执行次数最频繁的前N条 SQL 语句，帮助定位查询效率低下的问题，以便进行优化。
* 表文件分析：mysqlstat 可以列出访问次数最频繁的前N张表文件（.ibd），这有助于查找热点表和磁盘使用情况。
* 锁阻塞：工具可以显示当前被锁阻塞的 SQL 语句，帮助识别并解决锁相关的问题。
* 自动杀死当前锁阻塞的SQL
* 死锁信息：mysqlstat 可以提供关于死锁的信息，帮助 DBA 了解并解决死锁问题。
* 索引分析：它可以查找重复或冗余的索引，帮助优化索引使用和减少存储空间的占用。
* 连接数统计：工具可以统计应用端 IP 的连接数总和，有助于了解数据库的连接负载情况。
* 表大小统计：mysqlstat 可以提供库中每个表的大小统计信息，有助于了解表的存储占用情况。
* 快速找出没有主键的表
* Binlog 分析：它可以在高峰期分析哪些表的 TPS 较高，帮助定位性能瓶颈或优化热点表。
* 查看主从复制信息：工具可以提供主从复制状态和延迟情况，方便监控和管理主从复制环境。
---------------------------------------
* Real-time Monitoring: mysqlstat can monitor and display real-time metrics such as QPS, TPS, and network bandwidth usage of the MySQL server.

* Query Analysis: It can show the most frequently executed SQL statements, helping to identify and optimize queries with poor efficiency.

* Table File Analysis: mysqlstat can list the most frequently accessed table files (.ibd), aiding in identifying hot tables and disk usage.

* Lock Blocking: The tool can display the currently blocked SQL statements due to locks, assisting in identifying and resolving lock-related issues.

* Automatic killing of currently locked SQL statements.

* Deadlock Information: mysqlstat provides information about deadlocks, helping DBAs understand and resolve deadlock issues.

* Index Analysis: It can identify duplicate or redundant indexes, facilitating index optimization and reducing storage space consumption.

* Connection Count Statistics: The tool can provide statistics on the total number of connections from different application IPs, helping to understand the database's connection load.

* Table Size Statistics: mysqlstat can provide size statistics for each table in the database, aiding in understanding the storage occupation of tables.

* Binlog Analysis: It can analyze which tables have high TPS during peak periods, assisting in identifying performance bottlenecks or optimizing hot tables.

* Viewing Master-Slave Replication Information: The tool can provide information about the status and delay of the master-slave replication, facilitating monitoring and management of the replication environment.


# 原理
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/1d4791f9-5cb9-48e5-85b5-c97cb65cb89f)

---------------------------------------------
# 演示

https://www.douyin.com/video/7288887720057851151

# 使用
```
MySQL命令行监控工具 - mysqlstat

options:
  -h, --help            show this help message and exit
  -H MYSQL_IP, --mysql_ip MYSQL_IP
                        Mysql IP
  -P MYSQL_PORT, --mysql_port MYSQL_PORT
                        Mysql Port
  -u MYSQL_USER, --mysql_user MYSQL_USER
                        Mysql User
  -p MYSQL_PASSWORD, --mysql_password MYSQL_PASSWORD
                        Mysql Password
  --top  N              需要提供一个整数类型的参数值，该参数值表示执行次数最频繁的前N条SQL语句
  --io  N               需要提供一个整数类型的参数值，该参数值表示访问次数最频繁的前N张表文件ibd
  --lock                查看当前锁阻塞的SQL
  --kill                杀死当前锁阻塞的SQL
  --dead                查看死锁信息
  --index               查看重复或冗余的索引
  --conn                查看应用端IP连接数总和
  --tinfo               统计库里每个表的大小
  --fpk                 快速找出没有主键的表
  --binlog              Binlog分析-高峰期排查哪些表TPS比较高
  --repl                查看主从复制信息
  -v, --version         show program's version number and exit
```

- 实时监控mysql服务器的QPS、TPS、网络带宽指标（默认不加参数选项）
```
shell> chmod 755 mysqlstat  
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang'
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/9fb32687-147f-49b4-a89a-4f957ddb3648)


- 执行次数最频繁的前10条SQL语句
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --top 10
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/2475d034-c426-4921-97cd-d79f39af774a)

- 访问次数最频繁的前10张表文件ibd
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --io 10
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/a36b8117-a027-41cf-93e0-1fb6c74942eb)

- 查看当前锁阻塞的SQL
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --lock
或
shell> #杀死当前锁阻塞的SQL
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --lock --kill
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/e1cd1a6a-78a1-4fae-ace8-54f5fbfc34f9)

- 查看重复或冗余的索引
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --index
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/aebb781f-fcf0-4d41-8364-d381795913df)

- 查看应用端IP连接数总和
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --conn
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/8d3944ad-5c6b-45fb-8906-bc5495a45ba2)

- 统计库里每个表的大小
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --tinfo
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/2aa0d90b-02aa-42d1-b421-937ce794bb8d)

- 查看死锁信息
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --dead
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/2fb154d3-9d44-4eb1-9580-e43a22173dc0)

- Binlog分析-高峰期排查哪些表TPS比较高
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --binlog mysql-bin.000003
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/14ec7453-c5f1-4964-abef-69e04015abf8)

或者指定一个binlog范围
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --binlog  mysql-bin.000003  mysql-bin.000006
```
会统计mysql-bin.000003，mysql-bin.000004，mysql-bin.000005，mysql-bin.000006这4个文件

- 查看主从复制信息
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --repl
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/367617bd-983c-4625-970c-ef5f59f9dec0)

![image](https://github.com/hcymysql/mysqlstat/assets/19261879/67d99e88-c041-4394-b2a2-6845713979dd)

### 支持 MySQL5.7/8.0，工具适用于Centos7 系统。

### 8.0默认是caching_sha2_password用户认证，需要更改为 mysql_native_password
```
mysql> CREATE USER 'rd'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
mysql> GRANT ALL on *.* to 'rd'@'%';
```
