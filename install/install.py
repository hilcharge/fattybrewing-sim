#!/usr/bin/env python

"""This script installs the database"""

import os
import sqlite3
import sys

def usage():
    print("""Usage: install.py DBNAME""")



def main(args):
    if not args:
        usage()

        raise Exception("No filename given")

    filename=args[0]
    sql_src_dir=os.path.dirname(os.path.realpath(__file__))
    
    dest_file=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","var",filename)

    if not os.path.isdir(os.path.dirname(dest_file)):        
        os.makedirs(os.path.dirname(dest_file))            
    

    try:
        dbconn=sqlite3.connect(dest_file)
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(str(e)+" file: {0}".format(dest_file))

    schema_file=os.path.join(sql_src_dir,"fattybrewery-schema.sql")
    init_file=os.path.join(sql_src_dir,"fattybrewery-init.sql")

    for f in [schema_file,init_file]:
        if not os.path.isfile(f):
            raise OSError("Unable to find required file {0}".format(f))

    for f in [schema_file,init_file]:
        with open(f) as sfh:
            sql=sfh.read()
            dbconn.executescript(sql)
    
    dbconn.close()

if __name__=='__main__':
    main(sys.argv[1:])

