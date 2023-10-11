# MySQL命令行监控工具 - mysqlstat 介绍

#### mysqlstat 是一个命令行工具，用于实时监控和分析 MySQL 服务器的性能指标和相关信息。
#### 它可以帮助 DBA（数据库管理员）和开发人员定位和解决数据库性能问题。
#### 以下是 mysqlstat 工具的主要功能：
---------------------------------------------
* 实时监控mysql服务器的QPS、TPS、网络带宽指标
* 查看执行次数最频繁的前N条SQL语句
* 查看访问次数最频繁的前N张表文件ibd
* 查看当前锁阻塞的SQL
* 查看死锁信息
* 查看重复或冗余的索引
* 查看应用端IP连接数总和
* 统计库里每个表的大小
* Binlog分析-高峰期排查哪些表TPS比较高
---------------------------------------------
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
  --top TOP             需要提供一个整数类型的参数值，该参数值表示执行次数最频繁的前N条SQL语句
  --io IO               需要提供一个整数类型的参数值，该参数值表示访问次数最频繁的前N张表文件ibd
  --lock                查看当前锁阻塞的SQL
  --dead                查看死锁信息
  --index               查看重复或冗余的索引
  --conn                查看应用端IP连接数总和
  --tinfo               统计库里每个表的大小
  --binlog              Binlog分析-高峰期排查哪些表TPS比较高
  -v, --version         show program's version number and exit
```

# 使用
- 实时监控mysql服务器的QPS、TPS、网络带宽指标（默认不加参数选项）
```
shell> chmod 755 mysqlstat  
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang'
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/d8864b42-4f88-4d3b-9cde-c426c3d35cef)


- 执行次数最频繁的前10条SQL语句
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --top 10
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/11437da2-40c2-4ccf-8f9f-79d9d6f52d3d)

- 访问次数最频繁的前10张表文件ibd
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --io 10
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/025cc1d2-0548-464b-8e1a-1011ae06b6f2)

- 查看当前锁阻塞的SQL
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --lock
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/507639a7-92c0-452c-aa0c-dd0eb7653006)

- 查看重复或冗余的索引
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --index
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/5bbd1b57-7c46-4244-a916-7e61f2e7a55a)

- 查看应用端IP连接数总和
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --conn
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/cf0c1e44-7ab9-4aa0-9461-e4e927a51da7)

- 统计库里每个表的大小
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --tinfo
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/9b500c54-2db0-4f43-8d42-ca24f7a12223)

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

### 支持 MySQL5.7/8.0，工具适用于Centos7 系统。

### 8.0默认是caching_sha2_password用户认证，需要更改为 mysql_native_password
