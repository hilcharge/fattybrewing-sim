import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__),"..","lib"))

from fattybrewing import container

from datetime import datetime, timedelta

def test_mash_tun():
    
    mash_tun = container.MashTun((35,'L'))
    
    
    assert mash_tun.size.amount == 35
    assert mash_tun.size.unit.lower() == 'l'

    # add contents

    mash_tun.add_content('water', (10,'l'))
    
    assert mash_tun.contents[0].content == 'water'
    assert mash_tun.contents[0].amount == 10
    assert mash_tun.contents[0].unit.lower() == 'l'

    # Remove contents
    removed = mash_tun.remove_content('water', (3, 'l'))
    assert removed[0][1]["amount"] == 3
    assert mash_tun.contents[0].amount == 7

    # Set the temperature
    mash_tun.heat_contents((35,'C'))

    assert mash_tun.contents[0].temperature.degrees == 35
    assert mash_tun.contents[0].temperature.unit == 'C'
    
    removed = mash_tun.remove_content('water',(2,'l'))
    assert removed[0][2]["degrees"] == 35
    


class TestContentMovement:
    
    def setup(self):
        self.mash_tun = container.MashTun((50,'L'))
        self.big_fermenter = container.Fermenter((60,'L'))
        self.third_fermenter = container.Fermenter((30,'L'))
        self.second_fermenter = container.Fermenter((40,'L'))

    def test_single_move(self):
        
        self.mash_tun.add_content('water', (20, 'l'))
        self.mash_tun.add_content('malt', (5, 'l'))
        garbage = container.move_all(self.mash_tun, self.big_fermenter)
        assert not garbage
        print("Moved contents: %s" % self.big_fermenter.contents)
        assert self.big_fermenter.contents[0].content == 'water'
        assert self.big_fermenter.contents[1].content == 'malt'
        assert self.big_fermenter.contents[1].amount == 5
        assert self.big_fermenter.contents[1].unit == 'l'
        
    def test_converting_contents(self):
        
        self.mash_tun.add_content('water', (20, 'l'))
        self.mash_tun.add_content('malt', (1, 'kg'))
        self.mash_tun.heat_contents((70, 'C'))

        self.mash_tun.convert_to_wort()
        print("Contents: %s" % self.mash_tun.contents )
        assert "wort" in [ c.content for c in self.mash_tun.contents ]
        assert self.mash_tun.contents[0].amount == 20
        assert self.mash_tun.contents[0].unit == 'l'

        assert self.mash_tun.contents[1].content == 'used malt'
        
    def test_add_all(self):
        #contents_list=None
        
        contents = ('water', (20, 'l'), (35,'C'), ('malt', (1, 'kg')))
        self.mash_tun.add_all(contents)
                    
    def test_add_yeast(self):
    
        self.big_fermenter.add_content('wort', (30,'l'))
        self.big_fermenter.add_content('yeast', (50, 'g'))
        
        assert "yeast" in [ c.content for c in self.big_fermenter.contents ]

    def test_fermentation(self):
        
        self.big_fermenter.add_content('wort', (30,'l'))
        self.big_fermenter.add_content('yeast', (50, 'g'))
        self.big_fermenter.add_content('fragrance hops', (500, 'g'))
        self.big_fermenter.ferment_wort(timedelta(days=30))
        beers = [ c for c in self.big_fermenter.contents if c.content_type == container.ContentType.Beer ]
        assert len(beers) == 1
        assert beers[0].updated_datetime.date() == (datetime.now()+timedelta(days=30)).date()


    def test_kegging(self):
        self.big_fermenter.add_content('beer', (30, 'l'))
        self.big_fermenter.add_content('fragrance hops', (500, 'g'))

        kegs = [ container.Keg((20,'l')) for i in range(3)) ]
        garbage = self.big_fermenter.into_kegs(kegs)


        
