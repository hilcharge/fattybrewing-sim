import sys, os

import couchdb

sys.path.append(os.path.join(os.path.dirname(__file__),"..","lib"))

TEST_PORT = 9999

class TestCouchDB:

    @classmethod
    def setupClass(cls):
        cls.couchdb_server = couchdb.Server('http://localhost:{}'.format(TEST_PORT), "")
        
        cls.database = cls.couchdb_server.create('brewing-db-unittest')

    def test_store(self):
        
        doc = {'type': 'fermenter', 'name': 'test-fermenter'}
        
        self.database.save(doc)

        for id in self.database:
            assert self.databse.get(id)



        
