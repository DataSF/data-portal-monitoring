
# coding: utf-8
#!/usr/bin/env python

from PostgresStuff import *


def main():
    db_config = PostgresStuff.load_config()
    conn_alq, meta_alq =PostgresStuff.connect_alq(db_config)
    conn = PostgresStuff.connect()
    print conn



if __name__ == '__main__':
    main()