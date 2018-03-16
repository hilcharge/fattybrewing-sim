import unittest

import install
import os
import sqlite3


class TestInstallDB(unittest.TestCase):

    
    def setUp(self):
        self.dbfile=os.path.join(os.path.dirname(__file__),"brewery-test.db3")
        install.main(self.dbfile)
        self.dbconn=sqlite3.connect(self.dbfile)

    def test_container_exist(self):
        c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='containers'""")
        self.AssertEqual(c.fetchone()[0],"container")

    # def containerExist(self):
    #     c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='containers'""")

    # def containerExist(self):
    #     c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='containers'""")
        

    def tearDown(self):
        os.remove(os.path.join(os.path.dirname(__file__),"brewery-test.db3"))


if __name__=='__main__':
    unittest.main()
