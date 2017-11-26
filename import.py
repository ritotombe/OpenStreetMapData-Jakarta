# Adapted from http://www.sqlitetutorial.net/sqlite-python/creating-database/
# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error
import pandas as pd

import schema

SCHEMA = schema.schema
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)

        # conn.close()


def create_table_body(body, col, sch):

    if sch['type'] == 'integer':
        body += '%s INTEGER' % col
    elif sch['type'] == 'float':
        body += '%s REAL' % col
    else:
        body += '%s TEXT' % col

    if len(body) == 0:
        body += ' PRIMARY KEY,'
    elif sch['required']:
        body += ' NOT NULL,'
    else:
        body += ','

    return body


FILE_NAMES = ['node', 'node_tags', 'way', 'way_tags', 'way_nodes']
# FILE_NAMES = ['way_nodes']
if __name__ == '__main__':
    conn = create_connection('files/pythonsqlite.db')

    c = conn.cursor()

    for i, val in SCHEMA.items():
        body = ''
        for col, sch in val['schema'].items():
            body = create_table_body(body,col,sch)
        sql = 'CREATE TABLE IF NOT EXISTS %s (%s)' % (i, body[:-1])
        c.execute(sql)

    count = 0
    for obj in FILE_NAMES:
        print("1")
        objFile = pd.read_csv('files/%s.csv' % obj, encoding='utf-8')
        print("2")
        asciiHeader = list(objFile.columns.values)
        print("3")
        for i,head in enumerate(asciiHeader):
            asciiHeader[i] =  head.replace("b'","").replace("'","")
        objFile.columns = asciiHeader
        sch = SCHEMA[obj]['schema']
        columns = sch.keys()

        for i, row in objFile.iterrows():
            count += 1
            body = ''
            for col in columns:
                if sch[col]['type'] == 'integer':
                    if type(row[col]) is int:
                        body += " %d," % row[col]
                    else:
                        body += " %s," % row[col].replace("b'","").replace("'","")
                elif sch[col]['type'] == 'float':
                    body += " %s," % row[col].replace("b'","").replace("'","")
                else:
                    body += "'%s'," % row[col].replace("b'","").replace("'","")

            sql = "INSERT INTO %s (%s) VALUES (%s)" % (obj, ",".join(list(columns)), body[:-1])
            print(count)
            # print(sql)
            c.execute(sql)
        conn.commit()
