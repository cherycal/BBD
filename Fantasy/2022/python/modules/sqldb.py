from __future__ import print_function

__author__ = 'chance'

import inspect
import sqlite3
import sys
import time

import push
import tools

sys.path.append('./modules')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

import pandas as pd

import gspread
from gspread_dataframe import set_with_dataframe


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
        self.conn = sqlite3.connect(self.db, timeout=15)
        # print("Opening " + self.db)
        self.cursor = self.conn.cursor()
        self.msg = ""
        self.push_instance = push.Push()

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

    def execute(self, cmd, params, verbose=0):
        if verbose:
            print_calling_function(cmd)
        self.cursor.execute(cmd, params)
        self.conn.commit()

    def select(self, query, verbose=0):
        if verbose:
            print_calling_function(query)
        self.cursor.execute(query)
        self.conn.commit()
        return self.cursor.fetchall()

    def list(self, query, verbose=0):
        if verbose:
            print_calling_function(query)
        return [row[0] for row in self.select(query)]

    def select_plus(self, query, verbose=0):
        # returns:
        # - 'column_names': a list of column names
        # - 'rows': rows in query, ordered by columns as described in 'column_names'
        # - 'dicts': a list of dictionaries, each item in list is a
        #    dict representing a row in the query as key/value pairs ( column_name / row value )
        ret_dict = dict()
        if verbose:
            print_calling_function(query)
        self.cursor.execute(query)
        self.conn.commit()
        col_headers = list(map(lambda x: x[0], self.cursor.description))
        rows = list()
        dicts = list()
        for row in self.cursor.fetchall():
            rows.append(row)
            res = dict(zip(col_headers, list(row)))
            dicts.append(res)
        ret_dict['column_names'] = col_headers
        ret_dict['rows'] = rows
        ret_dict['dicts'] = dicts
        return ret_dict

    def select_table(self, table):
        return self.select_plus(f'SELECT * from {table}')

    def select_w_cols(self, query, verbose=0):
        if verbose:
            print_calling_function(query)
        self.cursor.execute(query)
        self.conn.commit()
        col_headers = list(map(lambda x: x[0], self.cursor.description))
        rows = list()
        for row in self.cursor.fetchall():
            rows.append(row)
        return col_headers, rows

    def insert(self, command, verbose=0):
        self.cmd(command, verbose)

    def insert_many(self, table_name, in_list):
        #
        # "in_list" is a list of tuples
        # Ex: db.insert_many( Animals, [ (1,'a','aardvark'),(2,'b','bear'),(3,'c','cat') ] )
        # each tuple must *precisely* match the columns in a table
        table = table_name
        # print_calling_function()
        # print("in_list[0]:")
        # print(in_list[0])
        question_mark_string = "("
        for _ in in_list[0]:
            question_mark_string += "?,"
        question_mark_string = question_mark_string[: -1] + ")"
        command = "INSERT INTO " + table + " VALUES " + question_mark_string
        # print(command)
        # print(in_list)
        try:
            self.conn.executemany(command, in_list)
            self.conn.commit()
        except Exception as ex:
            print(str(ex))
        return

    def insert_list(self, table, in_list, verbose=0):
        # inserts one row given a list of values that *precisely* matches the columns in a table
        # print_calling_function()
        # print(table)
        # print(in_list)

        try:
            cursor = self.conn.execute('select * from ' + table)
            out_list = list(map(lambda x: x[0], cursor.description))
            cols = self.string_from_list(out_list)
            # print(cols)
            question_mark_string = "("
            for _ in in_list:
                question_mark_string += "?,"
            # question_mark_string = question_mark_string[: -1] + ")"
            cmd = "INSERT INTO " + table + " ( " + cols + " ) VALUES (" + self.string_from_list2(in_list) + ")"
            if verbose:
                print(cmd)
            # self.conn.execute("INSERT INTO " + table +
            #                   " ( " + cols + " ) VALUES " +
            #                   question_mark_string, in_list)
            self.cmd(cmd, verbose)
            # self.cursor.execute(list)
            self.conn.commit()
            if verbose:
                print(f'inserted {in_list} into {table}')
        except Exception as ex:
            print(str(ex))

        return

    def update_list(self, table, set_attr, where_attr, params):
        # print_calling_function()
        # print(params)
        try:
            self.conn.execute("UPDATE " + table + " SET " +
                              set_attr + " = ? where " + where_attr + "= ?", params)
            self.conn.commit()
        except Exception as ex:
            print(str(ex))
        return

    def delete_item(self, command, params, verbose=0):
        if verbose:
            print_calling_function(command)
        self.cursor.execute(command, params)
        self.conn.commit()

    def delete(self, command, verbose=0):
        self.cmd(command, verbose)

    def update(self, command, verbose=0):
        self.cmd(command, verbose)

    def cmd(self, command, verbose=0):
        if verbose:
            print_calling_function(command)
        tries = 0
        max_tries = 2
        incomplete = 1
        while incomplete and tries < max_tries:
            try:
                self.cursor.execute(command)
                self.conn.commit()
                incomplete = 0
                if verbose:
                    print("DB command succeeded: " + command)
            except Exception as ex:
                print(str(ex) + ": " + command)
                tries += 1
                self.push_instance.push(title="DB command failed", body = f"{str(ex)}: {command}")
                time.sleep(2.5)
        if tries == max_tries:
            print("DB command failed: " + command)
            print_calling_function(command)

    def update_data(self, command, data, verbose=0):
        if verbose:
            print(command, data)
            print_calling_function(command)
        tries = 0
        max_tries = 5
        incomplete = 1
        while incomplete and tries < max_tries:
            try:
                self.cursor.execute(command, data)
                self.conn.commit()
                incomplete = 0
                if verbose:
                    print("DB command succeeded: " + command)
            except Exception as ex:
                print(str(ex))
                tries += 1
                self.push_instance.push(title="DB command failed", body = f"{str(ex)}: {command}")
                time.sleep(2.5)

        if tries == max_tries:
            print("DB command failed: " + command)
            print_calling_function(command)

    def table_or_view(self, name):
        query = f'SELECT count(*) FROM sqlite_master where  type in ("view", "table" ) and name = "{name}"'
        result = int(self.select(query)[0][0])
        return result > 0

    def table_to_csv(self, tblname):
        lol = []
        filename = f'./data/{tblname}.csv'
        if self.table_or_view(tblname):
            detail_history = self.select_plus(f'SELECT * FROM {tblname}')
            for row in detail_history['rows']:
                lol.append(row)
            detail_df = pd.DataFrame(lol, columns=detail_history['column_names'])
            detail_df.to_csv(filename)
            print(f'Created: {filename}')
        else:
            print(f'Table/view {tblname} does not exist. File {filename} not created')

    def table_to_df(self, tblname):
        lol = []
        detail_df = None
        if self.table_or_view(tblname):
            detail_history = self.select_plus(f'SELECT * FROM {tblname}')
            for row in detail_history['rows']:
                lol.append(row)
            detail_df = pd.DataFrame(lol, columns=detail_history['column_names'])
        else:
            print(f'Table/view {tblname} does not exist. df not created')
        return detail_df


    @tools.try_wrap
    def tables_to_sheets(self, table_name, worksheet_name):

        gc = gspread.service_account()
        try:
            sh = gc.open(worksheet_name)
            worksheet_title = "Sheet1"

            try:
                worksheet = sh.worksheet(worksheet_title)
                # Write a test DataFrame to the worksheet
                df_test = self.table_to_df(table_name)
                try:
                    set_with_dataframe(worksheet, df_test)
                    print(f"Sheet {worksheet_name}.{worksheet_title} published to sheets")
                except Exception as ex:
                    print(str(ex))
            except gspread.WorksheetNotFound:
                print(f"Sheet {worksheet_name}.{worksheet_title} not found")

        except gspread.SpreadsheetNotFound:
            print(f"Sheet {worksheet_name} not found")

    def close(self):
        # print("Closing " + self.db)
        self.conn.close()

    def string_from_list(self, in_list):
        self.msg = ""
        out_string = ""
        for i in in_list:
            out_string += i + ","
        out_string = out_string[:-1]
        return out_string

    def string_from_list2(self, in_list):
        self.msg = ""
        out_string = ""
        for i in in_list:
            out_string += "\"" + i + "\","
        out_string = out_string[:-1]
        return out_string
