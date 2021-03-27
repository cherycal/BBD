__author__ = 'chance'

import sqlite3
import tools
import inspect


# import logging


def print_calling_function(command='command left blank'):
    print(command)
    print(str(inspect.stack()))
    # print(str(inspect.stack()[-2].filename) + ", " + str(inspect.stack()[-2].function) +
    #                                                     ", " + str(inspect.stack()[-2].lineno))
    # print(str(inspect.stack()[1].filename) + ", " + str(inspect.stack()[1].function) +
    #       ", " + str(inspect.stack()[1].lineno))
    # print(str(inspect.stack()[-1].filename) + ", " + str(inspect.stack()[-1].function) +
    #       ", " + str(inspect.stack()[-1].lineno))
    return


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
        print("Opening " + self.db)
        self.cursor = self.conn.cursor()
        self.msg = ""

    def query(self, cmd, verbose=0):
        if verbose:
            print_calling_function(cmd)
        self.cursor.execute(cmd)
        self.conn.commit()
        columns = list()
        rows = list()
        for t in self.cursor.description:
            columns.append(t[0])
        for row in self.cursor.fetchall():
            rows.append(dict(zip(columns, row)))
        return rows

    def select(self, query, verbose=0):
        if verbose:
            print_calling_function(query)
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def select_w_cols(self, query, verbose=0):
        if verbose:
            print_calling_function(query)
        self.cursor.execute(query)
        self.conn.commit()
        col_headers = list(map(lambda x: x[0], self.cursor.description))
        rows = list()
        for row in self.cursor.fetchall():
            rows.append(row)
        return col_headers,rows

    def insert(self, command):
        print_calling_function(command)
        self.cursor.execute(command)
        self.conn.commit()

    def insert_many(self, table_name, in_list):
        #
        # "in_list" is a list of tuples
        # Ex: db.insert_many( Animals, [ (1,'a','aardvark'),(2,'b','bear'),(3,'c','cat') ] )
        # each tuple must *precisely* match the columns in a table
        table = table_name
        print_calling_function()
        # print("in_list[0]:")
        # print(in_list[0])
        question_mark_string = "("
        for _ in in_list[0]:
            question_mark_string += "?,"
        question_mark_string = question_mark_string[: -1] + ")"
        command = "INSERT INTO " + table + " VALUES " + question_mark_string
        # print(command)
        # print(in_list)
        self.conn.executemany(command, in_list)
        self.conn.commit()
        return

    def insert_list(self, table, in_list):
        # inserts one row given a list of values that *precisely* matches the columns in a table
        print_calling_function()
        # print(table)
        # print(in_list)
        cursor = self.conn.execute('select * from ' + table)
        out_list = list(map(lambda x: x[0], cursor.description))
        cols = self.string_from_list(out_list)
        # print(cols)
        question_mark_string = "("
        for _ in in_list:
            question_mark_string += "?,"
        question_mark_string = question_mark_string[: -1] + ")"
        self.conn.execute("INSERT INTO " + table + " ( " + cols + " ) "
                                                                  "VALUES " + question_mark_string, in_list)
        # self.cursor.execute(list)
        self.conn.commit()
        return

    def update_list(self, table, set_attr, where_attr, params):
        print_calling_function()
        # print(params)
        self.conn.execute("UPDATE " + table + " SET " +
                          set_attr + " = ? where " + where_attr + "= ?", params)
        self.conn.commit()
        return

    def delete_item(self, command, params):
        print_calling_function(command)
        print("In delete item")
        # print(command)
        # print(params)
        self.cursor.execute(command, params)
        self.conn.commit()

    def delete(self, command):
        print_calling_function(command)
        self.cursor.execute(command)
        self.conn.commit()

    def update(self, command):
        # print(command)
        print_calling_function(command)
        self.cursor.execute(command)
        self.conn.commit()

    def cmd(self, command):
        print(command)
        print_calling_function(command)
        self.cursor.execute(command)
        self.conn.commit()

    def update_data(self, command, data):
        print(command, data)
        print_calling_function(command)
        self.cursor.execute(command, data)
        self.conn.commit()

    def close(self):
        print("Closing " + self.db)
        self.conn.close()

    def string_from_list(self, in_list):
        self.msg = ""
        out_string = ""
        for i in in_list:
            out_string += i + ","
        out_string = out_string[:-1]
        return out_string
