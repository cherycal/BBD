__author__ = 'chance'

import sqlite3
import tools


class DB:

    def __init__(self, db):
        platform = tools.get_platform()
        if platform == "Windows":
            self.db = 'C:\\Ubuntu\\Shared\\data\\' + db
        elif platform == "linux" or platform == 'Linux':
            self.db = '/media/sf_Shared/data/' + db
        else:
            print("Platform " + platform + " not recognized in sqldb::DB. Exiting.")
            exit(-1)
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def query(self, cmd):
        self.cursor.execute(cmd)
        self.conn.commit()
        columns = list()
        rows = list()
        for t in self.cursor.description:
            columns.append(t[0])
        for row in self.cursor.fetchall():
            rows.append(dict(zip(columns, row)))
        return rows





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
        question_mark_string = "("
        for i in in_list:
            question_mark_string += "?,"
        question_mark_string = question_mark_string[: -1] + ")"
        self.conn.execute("INSERT INTO " + table + " ( " + cols + " ) "
                                        "VALUES " + question_mark_string, in_list)
        #self.cursor.execute(list)
        self.conn.commit()
        return

    @staticmethod
    def string_from_list(in_list):
        out_string = ""
        for i in in_list:
            out_string += i + ","
        return out_string[:-1]

    def delete(self, command):
        self.cursor.execute(command)
        self.conn.commit()

    def update(self, command):
        self.cursor.execute(command)
        self.conn.commit()

    def close(self):
        print("Closing " + self.db)
        self.conn.close()
