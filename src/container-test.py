import unittest

import container
import os
import sqlite3

class TestContainerMethods(unittest.TestCase):
    
    def setUp(self):
        self.newcontainer=container.BrewContainer(name="test container")
        self.dbfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","var","fattybrew-test.db3")
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",("test container",))
        dbconn.commit()
        dbconn.close()
        

    def test_new_container(self):
    
        self.assertTrue( isinstance(self.newcontainer ,container.BrewContainer))
        self.assertEqual(self.newcontainer.name,"test container")

    def test_total_volume(self):
        self.assertEqual(self.newcontainer.total_volume,1)
        self.assertEqual(self.newcontainer.total_volume_units,'unit-volume')
    def test_current_volume(self):
        self.assertEqual(self.newcontainer.current_volume,0)
        self.assertEqual(self.newcontainer.current_volume_units,'unit-volume')
    def test_current_temperature(self):
        self.assertEqual(self.newcontainer.current_temperature,1)        
        self.assertEqual(self.newcontainer.current_temperature_units,'unit-temperature')

    def test_target_temperature(self):
        self.assertEqual(self.newcontainer.target_temperature,1)
        self.assertEqual(self.newcontainer.target_temperature_units,'unit-temperature')
    def test_test_clean(self):
        self.assertFalse(self.newcontainer.clean)
        

    def test_store_container(self):
        self.newcontainer.store(dbfile=self.dbfile)

        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        
        c=dbconn.execute("""SELECT total_volume,total_volume_units,id,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean,name FROM containers WHERE name LIKE ?""",("test container",))
        
        r=c.fetchone()
        self.assertTrue(r)
        self.assertEqual(self.newcontainer.total_volume,r["total_volume"])
        self.assertEqual(self.newcontainer.total_volume_units,r["total_volume_units"])
        self.assertEqual(self.newcontainer.current_volume,r["current_volume"])
        self.assertEqual(self.newcontainer.current_volume_units,r["current_volume_units"])
        self.assertEqual(self.newcontainer.current_temperature,r["current_temperature"])
        self.assertEqual(self.newcontainer.current_temperature_units,r["current_temperature_units"])
        self.assertTrue(not self.newcontainer.clean and not r["clean"])
        
        self.assertEqual(self.newcontainer.name,r["name"])
        dbconn.commit()
        dbconn.close()
        
    def test_fill_container_with(self):
        self.newcontainer.fill_with(0.5,"unit-volume","water")

        self.assertEqual(self.newcontainer.current_volume,0.5)
        self.assertEqual(self.newcontainer.current_volume_units,"unit-volume")

    def test_overfill_container(self):
        cv=self.newcontainer.current_volume
        cv_units=self.newcontainer.current_volume_units
        new_vol=self.newcontainer.current_volume+1000000
        nv_units=self.newcontainer.current_volume_units

        self.assertRaises(container.OverflowError,self.newcontainer.fill_with,new_vol,nv_units,"water")
        
    def test_fill_container_to(self):
        self.newcontainer.current_volume=0.6
        self.newcontainer.current_volume_units="unit-volume"

        self.assertRaises(container.OverflowError, self.newcontainer.fill_to,0.5,"unit-volume","water")

        self.assertEqual(self.newcontainer.current_volume,0.6)


        self.newcontainer.fill_to(0.7,"unit-volume","water")
        self.assertEqual(self.newcontainer.current_volume,0.7)

        

    def test_add_ingredient(self):

        ingredient="generic malt"
        unit="unit-malt"
        self.newcontainer.add_ingredient(0.3,"unit-malt","generic malt")        
        self.assertTrue("generic malt" in self.newcontainer.contents["solids"])
        self.assertEqual( self.newcontainer.contents["solids"][ingredient][0]["amount"],0.3)
        self.assertEqual( self.newcontainer.contents["solids"][ingredient][0]["units"],"unit-malt")
        self.newcontainer.store(self.dbfile)
        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        c=dbconn.execute("""DELETE FROM container_contents WHERE container=?""",(self.newcontainer.bcid,))

        c=dbconn.execute("""SELECT containers.id,solid_ingredient,solid_ingredient_amount,solid_ingredient_amount_unit,ingredient_alias FROM 
containers 
LEFT JOIN container_contents ON container_contents.container = containers.id AND containers.id=? 
LEFT JOIN ingredients ON container_contents.solid_ingredient = ingredients.id """,(self.newcontainer.bcid,))        
        f=c.fetchone()
        
        self.assertEqual(f["id"],self.newcontainer.bcid)
        self.assertEqual(f["solid_ingredient_amount"],1.0)
        self.assertEqual(f["solid_ingredient_amount_unit"],"unit-malt")

        self.assertEqual(f["ingredient_alias"],"generic malt")

        dbconn.commit()
        dbconn.close()
        ## Now test ADDITIONAL ingredients
        
    def test_add_mult_ingredients(self):
        ingredients=[
            (0.3,"unit-malts","generic malt"),
                     (0.2,"unit-hops","generic hops"),
                     (0.2,"unit-yeast","generic yeast"),
                     (03.,"L","water")
                     ]            


        insert_sql="""INSERT INTO container_contents (solid_ingredient_amount,solid_ingredient_amount_unit,solid_ingredient) VALUES (?,?,(SELECT ingredient_alias FROM ingredients WHERE ingredients.ingredient_alias =?))"""

        sql="""SELECT ingredient_alias,solid_ingredient_amount,solid_ingredient_amount_unit FROM ingredients 
LEFT JOIN container_contents ON  container_contents.solid_ingredient = ingredients.id WHERE ingredients.ingredient_alias=? """

        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        for (a,u,i) in ingredients:
            ## Insert the ingredient into the container
            #print(insert_sql)
            c=dbconn.execute(insert_sql,(a,u,i))
            dbconn.commit()
            
        for (a,u,i) in ingredients:
            ## Insert the ingredient into the container
            c=dbconn.execute(sql,(i,))
            f=c.fetchone()
            self.assertEqual(f["ingredient_alias"],i)
            self.assertEqual(f["solid_ingredient_amount",a])
            self.assertEqual(f["solid_ingredient_amount_unit",u])
            

        dbconn.close()

        
    def tearDown(self):
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("pragma busy_timeout=20000")
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",("test container",))
        
        # try:
        #     os.remove(self.dbfile)
        # except OSError:
        #     pass
        dbconn.commit()
        dbconn.close()


class TestMashTunMethods(unittest.TestCase):
    
    def setUp(self):
        self.mashtunname="test mash tun"
        self.newmashtun=container.MashTun(name=self.mashtunname)
        self.dbfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","var","fattybrew-test.db3")
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM mash_tuns WHERE container IN (SELECT id from containers WHERE mash_tuns.container = containers.id AND containers.name=?)""",(self.newmashtun.name,))
        dbconn.commit()
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newmashtun.name,))
        dbconn.commit()
        dbconn.close()

    def test_new_mashtun(self):
    
        self.assertTrue( isinstance(self.newmashtun ,container.MashTun))


    def test_store(self):
        self.newmashtun.store(self.dbfile)
        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        
        c=dbconn.execute("""SELECT total_volume,total_volume_units,containers.id as container_id,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean,name,mash_tuns.id as mash_tun_id,containers.id as container_id FROM containers JOIN mash_tuns ON containers.id=mash_tuns.container WHERE name LIKE ?""",("test mash tun",))
        
        r=c.fetchone()
        self.assertTrue(r)
        self.assertEqual(self.newmashtun.total_volume,r["total_volume"])
        self.assertEqual(self.newmashtun.total_volume_units,r["total_volume_units"])
        self.assertEqual(self.newmashtun.current_volume,r["current_volume"])
        self.assertEqual(self.newmashtun.current_volume_units,r["current_volume_units"])
        self.assertEqual(self.newmashtun.current_temperature,r["current_temperature"])
        self.assertEqual(self.newmashtun.current_temperature_units,r["current_temperature_units"])
        self.assertTrue(not self.newmashtun.clean and not r["clean"])
        
        self.assertEqual(self.newmashtun.name,r["name"])

        self.assertEqual(self.newmashtun.bcid,r["container_id"])
        
        #dbconn=sqlite3.connect(self.dbfile)
        self.assertEqual(self.newmashtun.name,self.mashtunname)
        


        

        
        
        
        
                         
        
    

    def tearDown(self):
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM mash_tuns WHERE container IN (SELECT id from containers WHERE mash_tuns.container = containers.id AND containers.name=?)""",(self.newmashtun.name,))
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newmashtun.name,))
        dbconn.commit()
        dbconn.close()



class TestFermenterMethods(unittest.TestCase):
    
    def setUp(self):
        self.fermentername="test fermenter"
        self.newfermenter=container.Fermenter(name=self.fermentername)
        self.dbfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","var","fattybrew-test.db3")
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM mash_tuns WHERE container IN (SELECT id from containers WHERE mash_tuns.container = containers.id AND containers.name=?)""",(self.newfermenter.name,))
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newfermenter.name,))
        dbconn.commit()
        dbconn.close()

        

    def test_new_mashtun(self):
    
        self.assertTrue( isinstance(self.newfermenter ,container.Fermenter))


    def test_store(self):
        self.newfermenter.store(self.dbfile)
        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        
        c=dbconn.execute("""SELECT total_volume,total_volume_units,containers.id as container_id,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean,name,fermenters.id FROM containers JOIN fermenters ON containers.id=fermenters.container WHERE name LIKE ?""",(self.fermentername,))
        
        r=c.fetchone()
        self.assertTrue(r)
        self.assertEqual(self.newfermenter.total_volume,r["total_volume"])
        self.assertEqual(self.newfermenter.total_volume_units,r["total_volume_units"])
        self.assertEqual(self.newfermenter.current_volume,r["current_volume"])
        self.assertEqual(self.newfermenter.current_volume_units,r["current_volume_units"])
        self.assertEqual(self.newfermenter.current_temperature,r["current_temperature"])
        self.assertEqual(self.newfermenter.current_temperature_units,r["current_temperature_units"])
        self.assertTrue(not self.newfermenter.clean and not r["clean"])
        
        self.assertEqual(self.newfermenter.name,r["name"])

        self.assertEqual(self.newfermenter.bcid,r["container_id"])
        
        #dbconn=sqlite3.connect(self.dbfile)
        self.assertEqual(self.newfermenter.name,self.fermentername)
        

                         
        
    

    def tearDown(self):
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM fermenters WHERE container IN (SELECT id from containers WHERE fermenters.id = containers.id AND containers.name=?)""",(self.newfermenter.name,))
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newfermenter.name,))
        


class TestLiquidReservoirMethods(unittest.TestCase):
    
    def setUp(self):
        self.liquidresname="test liquid reservoir"
        self.newliquidres=container.LiquidReservoir(name=self.liquidresname)
        self.dbfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","var","fattybrew-test.db3")
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM liquid_reservoirs WHERE container = (SELECT id from containers WHERE liquid_reservoirs.id = containers.id AND containers.name=?)""",(self.newliquidres.name,))
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newliquidres.name,))
        dbconn.commit()
        dbconn.close()
        

    def test_new_liquid_reservoir(self):
    
        self.assertTrue( isinstance(self.newliquidres ,container.LiquidReservoir))


    def test_store(self):
        self.newliquidres.store(self.dbfile)
        dbconn=sqlite3.connect(self.dbfile)
        dbconn.row_factory=sqlite3.Row
        
        c=dbconn.execute("""SELECT total_volume,total_volume_units,containers.id as container_id,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean,name,liquid_reservoirs.id FROM containers JOIN liquid_reservoirs ON containers.id=liquid_reservoirs.container WHERE name LIKE ?""",(self.liquidresname,))
        
        r=c.fetchone()
        self.assertTrue(r)
        self.assertEqual(self.newliquidres.total_volume,r["total_volume"])
        self.assertEqual(self.newliquidres.total_volume_units,r["total_volume_units"])
        self.assertEqual(self.newliquidres.current_volume,r["current_volume"])
        self.assertEqual(self.newliquidres.current_volume_units,r["current_volume_units"])
        self.assertEqual(self.newliquidres.current_temperature,r["current_temperature"])
        self.assertEqual(self.newliquidres.current_temperature_units,r["current_temperature_units"])
        self.assertTrue(not self.newliquidres.clean and not r["clean"])
        
        self.assertEqual(self.newliquidres.name,r["name"])

        self.assertEqual(self.newliquidres.bcid,r["container_id"])
        
        #dbconn=sqlite3.connect(self.dbfile)
        self.assertEqual(self.newliquidres.name,self.liquidresname)
        
    

    def tearDown(self):
        dbconn=sqlite3.connect(self.dbfile)
        c=dbconn.execute("""DELETE FROM liquid_reservoirs WHERE container = (SELECT id from containers WHERE liquid_reservoirs.id = containers.id AND containers.name=?)""",(self.newliquidres.name,))
        c=dbconn.execute("""DELETE FROM containers WHERE name LIKE ?""",(self.newliquidres.name,))
        dbconn.commit()
        dbconn.close()


if __name__=='__main__':
    unittest.main()

