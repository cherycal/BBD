__author__ = 'chance'
import sqlite3
import tools


class DB:

    def __init__(self, db):
        platform = tools.get_platform()
        if (platform == "Windows"):
            self.db = 'C:\\Ubuntu\\Shared\\data\\' + db
        elif (platform == "linux"  or platform == 'Linux'):
            self.db = '/media/sf_Shared/data/' + db
        else:
            print("Platform " + platform + " not recognized in sqldb::DB. Exiting.")
            exit(-1)
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()


    def select(self, query):
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def insert(self, command):
        self.cursor.execute(command)
        self.conn.commit()

    def insert_list(self, table, in_list):
        print(table)
        print(in_list)
        cursor = self.conn.execute('select * from ' + table)
        out_list = list(map(lambda x: x[0], cursor.description))
        cols = self.string_from_list(out_list)
        self.conn.execute("INSERT INTO " + table + " ( " + cols + " ) "
                  "VALUES (?,?,?)", in_list)
        #self.cursor.execute(list)
        self.conn.commit()
        return

    def string_from_list(self,in_list):
        out_string = ""
        for i in in_list:
            out_string += i+","
        return out_string[:-1]

    def delete(self, command):
        self.cursor.execute(command)
        self.conn.commit()

    def close(self):
        print("Closing " + self.db)
        self.conn.close()
