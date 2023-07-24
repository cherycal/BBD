__author__ = 'chance'

import sqldb

db = sqldb.DB('bdb.db')
table = 'A_Test'
list = ['8/2/2019','1223','foobar']

db.insert_list(table,list)