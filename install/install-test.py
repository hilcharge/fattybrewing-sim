import unittest

import install
import os
import sqlite3


class TestInstallDB(unittest.TestCase):
    
    def setUp(self):
        self.dbfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"brewery-test.db3")
        install.main([self.dbfile])
        self.dbconn=sqlite3.connect(self.dbfile)

    def test_containers_table_exist(self):
        c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type LIKE 'table'""")
        results=list(c.fetchall())

        for t in ["containers","fermenters","mash_tuns","liquid_reservoirs"]:
            self.assertTrue(t in [ r[0] for r in results ])

    def test_mash_tuns_exists(self):
        
        c=self.dbconn.execute("""SELECT container FROM mash_tuns""")
        results=c.fetchone()
        self.assertTrue(len(results) >=1 )

    def test_fermenter_exists(self):
        
        c=self.dbconn.execute("""SELECT container FROM fermenters""")
        results=c.fetchone()
        self.assertTrue(len(results) >=1 )

    def test_liquid_reservoir_exists(self):
        c=self.dbconn.execute("""SELECT container FROM liquid_reservoirs""")
        results=c.fetchone()
        self.assertTrue(len(results) >=1 )

        
    def ingredient_tables_exist(self):
        c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type LIKE 'table'""")
        results=list(c.fetchall())

        for t in ["ingredients","yeast_inventory","hops_inventory","malt_inventory"]:
            self.assertTrue(t in [ r[0] for r in results ])


    def test_ingredients_exist(self):

        c=self.dbconn.execute("""SELECT ingredient from yeast_inventory""")
        results=c.fetchone()
        self.assertTrue(results[0] >= 1)

        c=self.dbconn.execute("""SELECT ingredient from malt_inventory""")
        results=c.fetchone()
        self.assertTrue(results[0] >= 1)

        c=self.dbconn.execute("""SELECT ingredient from hops_inventory""")
        results=c.fetchone()
        self.assertTrue(results[0] >= 1)


        c=self.dbconn.execute("""SELECT ingredient from hops_inventory""")
        results=c.fetchone()
        self.assertTrue(results[0] >= 1)


    def test_water_exists(self):
        c=self.dbconn.execute("""SELECT name,liquid_type FROM liquids WHERE liquid_type LIKE 'purified_water' """)
        results=list(c.fetchone())
        self.assertTrue(results[0] >= 1)
        # for t in ["yeast_inventory","hops_inventory","malt_inventory"]:
        #     c= self.dbconn.execute("""SELECT ingredient from {0}""".format(t))
        #     results=list(c.fetchall())
        
        #     self.assertTrue()

    

    # def containerExist(self):
    #     c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='containers'""")

    # def containerExist(self):
    #     c= self.dbconn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='containers'""")
        

    def tearDown(self):
        pass
        #os.remove(os.path.join(os.path.dirname(__file__),"brewery-test.db3"))


if __name__=='__main__':
    unittest.main()
