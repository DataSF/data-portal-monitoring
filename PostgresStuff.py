# coding: utf-8
#!/usr/bin/env python


import psycopg2
from configparser import ConfigParser
import sqlalchemy
import re
import sys


class PostgresStuff:

    @staticmethod
    def load_config(filename=None, section='postgresql'):
        print ("****inside***")
        print (filename)
        if filename is None:
            filename='configs/database.ini'
        # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)
        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            #raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    
            print ("ERROR: No config file found")
            return False
        return db


    @staticmethod
    def connect(db_ini=None):
        """ Connect to the PostgreSQL database server """
        conn = None
        curr = None
        try:
            # read connection parameters
            params = PostgresStuff.load_config(db_ini)
            print (params)

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)

            # create a cursor
            cur = conn.cursor()

            # execute a statement
            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        return conn

    def close_connection():
        if conn is not None:
            conn.close()
            print('Database connection closed.')

    @staticmethod
    def connect_alq(db_ini):
        '''Returns a connection and a metadata object'''
        # We connect with the help of the PostgreSQL URL
        # postgresql://federer:grandestslam@localhost:5432/tennis
        conn = None
        meta = None
        db_config = PostgresStuff.load_config(db_ini)
        url = 'postgresql://{}:{}@{}:{}/{}'
        url = url.format(db_config['user'], db_config['password'], db_config['host'], db_config['port'], db_config['database'])
        try:
            # The return value of create_engine() is our connection object
            conn = sqlalchemy.create_engine(url, client_encoding='utf8')
            # We then bind the connection to MetaData()
            meta = sqlalchemy.MetaData(bind=conn, reflect=True)
        except (Exception ) as e:
            print str(e)

        return conn, meta

    @staticmethod
    def get_results(cur, row_cnt=None):
        result =  None
        result = cur.fetchmany(row_cnt)
        return result

    @staticmethod
    def select_records(conn, qry, row_cnt=None):
        """ query part and vendor data from multiple tables"""
        result = None
        try:
            cur = conn.cursor()
            cur.execute(qry)
            result = PostgresStuff.get_results(cur, row_cnt)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if cur is not None:
                cur.close()
        return result

    @staticmethod
    def update_records(conn, qry):
        return PostgresStuff.commitQry(conn, qry)
        #updt_rows = 0
        #try:
        #    cur = conn.cursor()
            # execute the UPDATE  statement
        #    cur.execute(qry)
        #    updt_rows = cur.rowcount
            # Commit the changes to the database
        #    conn.commit()
            # Close communication with the PostgreSQL database
        #    cur.close()
        #except (Exception, psycopg2.DatabaseError) as error:
        #    print(error)
        #finally:
        #    if cur is not None:
        #        cur.close()
        #return updt_rows

    @staticmethod
    def drop_table(conn, tblname):
        qry =  '''DROP TABLE IF EXISTS %s''' % (tblname)
        return PostgresStuff.commit_qry(conn, qry)

    @staticmethod
    def add_col_index(conn, index_name, tbl_name, index_col):
        drop_index_qry = '''DROP INDEX IF EXISTS %s ''' %(index_name)
        drop_index = PostgresStuff.commit_qry(conn, drop_index_qry)
        create_index_qry =  '''CREATE INDEX %s ON %s(%s)''' % (index_name, tbl_name, index_col)
        return PostgresStuff.commit_qry(conn, create_index_qry)


    @staticmethod
    def insertRecord(conn, tbl_name, header, values):
        qry = ' INSERT INTO ' +  tbl_name  + ' ( ' + ", ".join(header) + ' ) VALUES (' + ",".join(values) + ") ;"
        try:
            inserted_rows = PostgresStuff.commitQry(conn, qry)
        except (Exception) as e:
            print ("******")
            print str(e)
            print ("ERROR: could not insert record")
            print (qry)
            print ("*****")
        return inserted_rows
    

    @staticmethod
    def commitQry(conn, qry):
        updt_rows = 0
        try:
            cur = conn.cursor()
            # execute the UPDATE  statement
            cur.execute(qry)
            updt_rows = cur.rowcount
            # Commit the changes to the database
            conn.commit()
            # Close communication with the PostgreSQL database
            #print "** success**"
            #print qry
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(str(error))
            print ("***ERROR: could not excute qry*****")
            print (qry)
            print 
            return (error)
            print ("*****")
        finally:
            if cur is not None:
                cur.close()
        return updt_rows

    @staticmethod
    def terminateAllSessionsExceptCurrent(conn, db_name):
        qry = '''SELECT
                    pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE
                 -- don't kill current connection!
                    pid <> pg_backend_pid()
                    -- don't kill the connections to other databases
                    AND datname = '%s' ''' %(db_name)
        return PostgresStuff.commitQry(conn, qry)

    @staticmethod
    def variablize(text, prefix=''):
        if not prefix:
            # if no prefix, move any digits or non-word chars to the end
            parts = re.match('(^[\W\d]*)(.*$)', text).groups()
            text = "%s %s" % (parts[1], parts[0])
        text = ("%s %s" % (prefix, text)).strip().lower()
        text =  re.sub('[\W]', '_', text)
        return re.sub('_*$', '', text)

    @staticmethod
    def getColumnsFromInfile(infile, delimiter):
        return map(PostgresStuff.variablize, file(infile).readline().split( delimiter))

    @staticmethod
    def makeTableFromFileHeader(infile, delimiter, extraColumns=[]):
        columns = PostgresStuff.getColumnsFromInfile(infile, delimiter)
        columns = map(lambda v: '%s varchar(250)' % v, columns)
        columns = columns + extraColumns
        return columns

    @staticmethod
    def copyFileToDB(conn, infile, tblname, delimiter, columns=None):
        '''Read data from the file-like object file appending them to the table named table.
           Columns – iterable with name of the columns to import. The length and types should match the content of the file to read. If not specified, it is assumed that the entire table matches the file structure.'''
        cur = conn.cursor()
        finfile = open(infile, "r")
        if not(columns):
            cur.copy_from(
                finfile, tblname, delimiter
            )
        else:
            print "in here"
            cur.copy_from(
                finfile, tblname, delimiter, columns=columns
            )
        conn.commit()
        finfile.close()

    @staticmethod
    def copyTable(conn, existing_tblname, tblname):
        drp = PostgresStuff.drop_table(conn, tblname)
        qry = "CREATE table %s as select * from %s;" %(tblname, existing_tblname)
        print (qry)
        return PostgresStuff.commitQry(conn, qry)

if __name__ == '__main__':
    main()
