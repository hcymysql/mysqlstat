# MySQL命令行监控工具 - mysqlstat 介绍

#### mysqlstat 是一个命令行工具，功能如下：
* 实时监控mysql服务器的QPS、TPS、网络带宽指标。
* 查看执行次数最频繁的前N条SQL语句。
* 查看访问次数最频繁的前N张表文件ibd。
* 查看当前锁阻塞的SQL。
* 查看重复或冗余的索引。
* 查看应用端IP连接数总和。
* 统计库里每个表的大小。

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
  --index               查看重复或冗余的索引
  --conn                查看应用端IP连接数总和
  --tinfo               统计库里每个表的大小
  -v, --version         show program's version number and exit
```

# 使用
- 实时监控mysql服务器的QPS、TPS、网络带宽指标（默认不加参数选项）
```
shell> chmod 755 mysqlstat  
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang'
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/d8864b42-4f88-4d3b-9cde-c426c3d35cef)


- 增加参数选项，例如--top 10（执行次数最频繁的前10条SQL语句）
```
shell> ./mysqlstat -H 192.168.198.239 -P 6666 -u admin -p 'hechunyang' --top 10
```
![image](https://github.com/hcymysql/mysqlstat/assets/19261879/11437da2-40c2-4ccf-8f9f-79d9d6f52d3d)

