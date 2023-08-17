# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 13:13:07 2021

@author: Administrator
"""

"此文件用来查询mysql中的表和字段以及数据等等————代替其他工具进行查询"

import pymysql
import pandas as pd



"具体表中的数据"
database = 'project'   #表空间
table_name = 'data_classify'    #表名    sharp_and_standard     drowback_ranking

con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database=database)


ss_sql = 'SELECT * FROM {}.{};'.format(database,table_name)
ss = pd.read_sql(ss_sql,con)





# ss_sql = 'SELECT * FROM {} WHERE date in ("2022-09-16");'.format(table_name)
# ss = pd.read_sql(ss_sql,con)

# ss.to_sql('cyb_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='replace',index=False)

con.close()


ss.to_excel('{}.xlsx'.format(table_name),index=False)




aa = ss[ss['id']=='002772']

"查看所有表空间"
database_sql = 'SHOW DATABASES'
database = pd.read_sql(database_sql,con)


"表空间下有哪些表"
tables_sql = 'SHOW TABLES'
tables = pd.read_sql(tables_sql,con)

"表字段"
field_sql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '{}'".format(table_name)
field = pd.read_sql(field_sql,con)





"查看空间大小"
"查看表空间下某表的大小"
cursor = con.cursor()
cursor.execute("use information_schema;")
data_length_sql = "select data_length/1024,index_length from tables where table_schema='{}' and table_name = '{}';".format(database,table_name)
data_length = pd.read_sql(data_length_sql,con)


"查看某表空间大小"
data_length_sql = "select  table_schema as '数据库',  sum(table_rows) as '记录数',  sum(truncate(data_length/1024/1024, 2)) as '数据容量(MB)',  sum(truncate(index_length/1024/1024, 2)) as '索引容量(MB)'  from information_schema.tables  where table_schema='{}'; ".format(database)
data_length = pd.read_sql(data_length_sql,con)


