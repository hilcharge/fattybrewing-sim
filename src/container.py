"""This is a Python module for handling containers related to beer brewing. 


"""
import sqlite3
import os
import re
import datetime

class OverflowError(Exception):
    def __init__(self,message,errors):
        
        super(OverflowError,self).__init__(message)

        self.errors=errors
    

class BrewContainer:
    """ A class for handling brew containers

"""
    def __init__(self,name='',total_volume=1,total_volume_units='unit-volume',current_volume=0,current_volume_units='unit-volume',target_temperature=1,target_temperature_units='unit-temperature',current_temperature=1,current_temperature_units="unit-temperature",clean=False,id=None):
        self.total_volume=total_volume
        self.total_volume_units=total_volume_units
        self.bcid=id
        self.current_volume=current_volume
        self.current_volume_units=current_volume_units 
        self.target_temperature=target_temperature
        self.target_temperature_units=target_temperature_units
        self.current_temperature=current_temperature
        self.current_temperature_units=current_temperature_units
        self.clean=clean
        self.name=name
        self.contents={ ## A pack of its contents, in tuples of amount, liquid or ingredient
            "liquids": {},
            "solids": {}
            }

    def add_ingredient(self,amount,units,ingredient,fill_time=None):
        """ Adds a SOLID ingredient into the container. Does NOT consider volume """

        if not fill_time:
            fill_time=datetime.datetime.now()

        if ingredient in self.contents["solids"]:
            self.contents["solids"][ingredient].append({"amount": amount,
                                                                                                  "units": units,
                                                                                                  "time-added": fill_time})

        else:
            self.contents["solids"][ingredient]=[{"amount": amount,
                                              "units": units,
                                              "time-updated":fill_time,}]
        
        #self.current_volume=self.current_volume+self.contents["solids"][ingredient]["volume"]
 

    def fill_to(self,volume,units,liquid,fill_time=None):
        """
        Determine the amount of liquid to add into the container, then fill_with that amount.
        If the target amount is below the current volume, dont add anything and throw an error
        """

        if units != self.current_volume_units:
            (volume,units)=convert_units(volume,units,self.current_volume_units)
        if self.current_volume > volume:
            raise OverflowError("Unable to fill, as current volume {0}{1} greater than requested volume {2}".format(self.current_volume,self.current_volume_units,volume),[])
        required_volume=volume-self.current_volume
        
        self.fill_with(required_volume,units,liquid,fill_time)
        
        
        

    def fill_with(self,volume,units,liquid,fill_time=None):
        """ attempt to put volume units amount of liquid into the container. Raise an OverflowError if not possible, but still fill up the container """

        if not fill_time:
            fill_time=datetime.datetime.now()
        if (self.current_volume_units != units):
            (volume,units)=convert_units(volume,units,self.current_volume_units)
        if (self.current_volume + volume > self.total_volume ):
            wasted=abs(self.total_volume-(self.current_volume+volume))
            
            self.current_volume=self.total_volume

            raise OverflowError("unable to put all contents into container",[wasted,units])
        elif liquid in self.contents["liquids"]:
            self.contents["liquids"][liquid]["volume"]=self.contents["liquids"][liquid]["volume"]+volume
            self.contents["liquids"][liquid]["date-updated"]=fill_time
            self.current_volume=self.current_volume+self.contents["liquids"][liquid]["volume"]
        else:
            ##
            self.contents["liquids"][liquid]={"volume": volume,
                                              "units": units,
                                              "date-updated":fill_time,}
            self.current_volume=self.current_volume+self.contents["liquids"][liquid]["volume"]
                                              
        
        
    def store(self,dbfile=None):
        """Store the container into the given database"""

        if not os.path.isdir(os.path.dirname(dbfile)):
            raise OSError("Unable to save DB to file '{0}'".format(dbfile))
            
        if not os.path.isfile(dbfile):
           raise OSError("Unable to save DB to file '{0}'".format(dbfile)) 
        

        dbconn=sqlite3.connect(dbfile)
        dbconn.row_factory=sqlite3.Row
        ### Check if value is already stored

        ## Ifthe ID exists, assume it exists. Otherwise, assume a new record should be inserted
        if not self.bcid:

            c=dbconn.execute("""INSERT INTO containers (name,total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean) VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean))
            c=dbconn.execute("""SELECT max(id) FROM containers""")
            self.bcid=c.fetchone()[0]

        else:
            c=dbconn.execute("""UPDATE containers SET name=?,total_volume=?,total_volume_units=?,current_volume=?,current_volume_units=?,target_temperature=?,target_temperature_units=?,current_temperature=?,current_temperature_units=?,clean WHERE id = ?""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean,self,bcid))

            

    
        dbconn.commit()
        dbconn.close()


class Fermenter(BrewContainer):
    
    def store(self,dbfile):
        dbconn=sqlite3.connect(dbfile)

        dbconn.row_factory=sqlite3.Row
        ### Check if value is already stored

        ## Ifthe ID exists, assume it exists. Otherwise, assume a new record should be inserted
        if not self.bcid:

            c=dbconn.execute("""INSERT INTO containers (name,total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean) VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean))
            c=dbconn.execute("""SELECT max(id) FROM containers""")
            rowid=c.fetchone()[0]
            self.bcid=rowid
            c=dbconn.execute("""INSERT INTO fermenters (container) VALUES (?)""",(rowid,))            

        else:
            c=dbconn.execute("""UPDATE containers SET name=?,total_volume=?,total_volume_units=?,current_volume=?,current_volume_units=?,target_temperature=?,target_temperature_units=?,current_temperature=?,current_temperature_units=?,clean WHERE id = ?""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean,self,bcid))
    
        dbconn.commit()
        dbconn.close()


class MashTun(BrewContainer):
    def store(self,dbfile):
        dbconn=sqlite3.connect(dbfile)

        dbconn.row_factory=sqlite3.Row
        ### Check if value is already stored

        ## Ifthe ID exists, assume it exists. Otherwise, assume a new record should be inserted
        if not self.bcid:

            c=dbconn.execute("""INSERT INTO containers (name,total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean) VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean))
            c=dbconn.execute("""SELECT max(id) FROM containers""")
            rowid=c.fetchone()[0]
            self.bcid=rowid
            c=dbconn.execute("""INSERT INTO mash_tuns (container) VALUES (?)""",(rowid,))

            

        else:
            c=dbconn.execute("""UPDATE containers SET name=?,total_volume=?,total_volume_units=?,current_volume=?,current_volume_units=?,target_temperature=?,target_temperature_units=?,current_temperature=?,current_temperature_units=?,clean WHERE id = ?""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean,self,bcid))

        dbconn.commit()
        dbconn.close()




class LiquidReservoir(BrewContainer):
    def store(self,dbfile):
        dbconn=sqlite3.connect(dbfile)

        dbconn.row_factory=sqlite3.Row
        ### Check if value is already stored

        ## Ifthe ID exists, assume it exists. Otherwise, assume a new record should be inserted
        if not self.bcid:

            c=dbconn.execute("""INSERT INTO containers (name,total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean) VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean))
            c=dbconn.execute("""SELECT max(id) FROM containers""")
            rowid=c.fetchone()[0]
            self.bcid=rowid
            c=dbconn.execute("""INSERT INTO liquid_reservoirs (container) VALUES (?)""",(self.bcid,))

            

        else:
            c=dbconn.execute("""UPDATE containers SET name=?,total_volume=?,total_volume_units=?,current_volume=?,current_volume_units=?,target_temperature=?,target_temperature_units=?,current_temperature=?,current_temperature_units=?,clean WHERE id = ?""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean,self,bcid))
    
        dbconn.commit()
        dbconn.close()


class MashTun(BrewContainer):
    def store(self,dbfile):
        dbconn=sqlite3.connect(dbfile)
        dbconn.row_factory=sqlite3.Row
        ### Check if value is already stored

        ## Ifthe ID exists, assume it exists. Otherwise, assume a new record should be inserted
        if not self.bcid:
            #print("Inserting a mash tun container with name {0}".format(self.name))
            c=dbconn.execute("""INSERT INTO containers (name,total_volume,total_volume_units,current_volume,current_volume_units,target_temperature,target_temperature_units,current_temperature,current_temperature_units,clean) VALUES (?,?,?,?,?,?,?,?,?,?)""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean))
            if not c.rowcount:
                raise Exception("unable to insert a new row")
            
            c=dbconn.execute("""SELECT max(id) FROM containers""")
            rowid=c.fetchone()[0]
            self.bcid=rowid
            #print("Inserting a real mash tun for id",rowid)
            c=dbconn.execute("""INSERT INTO mash_tuns (container) VALUES (?)""",(self.bcid,))
            
            

        else:
            c=dbconn.execute("""UPDATE containers SET name=?,total_volume=?,total_volume_units=?,current_volume=?,current_volume_units=?,target_temperature=?,target_temperature_units=?,current_temperature=?,current_temperature_units=?,clean WHERE id = ?""",(self.name,self.total_volume,self.total_volume_units,self.current_volume,self.current_volume_units,self.target_temperature,self.target_temperature_units,self.current_temperature,self.current_temperature_units,self.clean,self,bcid))

        dbconn.commit()
        dbconn.close()


class EquipmentData:
    def __init__(datafile):
        
        if not datafile:
            datafile=os.path.join(os.environ["FATTYBREWHOME"],"var","fattybrew.db")
        if os.path.exists(datafile):
            self.conn=sqlite3.connect(datafile)
        else:
            raise Exception("Unable to make a database connection to {0}".format(datafile))
        self.datafile=datafile
            

def find_container(container_name_regex=None,other_fields={},dataset=None):
    """ Return a container from a name"""
    ## Load the database to find the container

    dbconn=EquipmentData(dataset)
    container=None
    chosen=0

    while not chosen:
        results=[]
        
        if container_name_regex:
            dbstr='''SELECT id FROM containers WHERE containers.name LIKE ?'''


            dbconn.execute(dbstr,container_name_regex)
            ## if not container_name_regex:
            ##     select from a list

            dbconn.execute('''SELECT id FROM containers WHERE containers.name LIKE ?''',container_name_regex)

            results=dbconn.fetchall()

        else: 
            dbstr='''SELECT id,name FROM container'''
            dbconn.execute(dbstr)
            results=dbconn.fetchall()
        if len(results) == 1:
            chosen=results[0][1]
        elif len(results) == 0:
            raise Exception("Unable to find any container")
        else:
            for r in results:
                print(r[0]," : ",r[1])

            while not 0 < chosen < len(results):                
                try:
                    chosen=results[input("Make your selection: ")][1]
                except ValueError,KeyError:
                    pass
                
        dbconn.execute('''SELECT total_volume,total_volume_units,current_volumen,current_volume_unit,
        target_temperature,target_temperature_units,id,name
        FROM containers WHERE containers.rowid LIKE ?''',chosen)
        results=dbconn.fetchall()
    cont=BrewContainer()




def convert_units(in_amount,in_volume,target_units):
    raise NotImplementedError

