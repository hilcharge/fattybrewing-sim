"""container module for fattybrewing

fattybrewing.container offers container classes and some functions

Synopsis:
-----------

from fattybrewing import container

# Define a mash tun

mash_tun = container.MashTun((35,'L'))

# Fill the container with something

mash_tun.




"""

from couchdb.mapping import Document, TextField, FloatField, IntegerField, DateTimeField, DecimalField, DictField, Mapping, ListField, BooleanField
from datetime import datetime
import logging

LOGGER = logging.getLogger("fattybrewing-container")
LOGGER.setLevel(logging.DEBUG)

WEIGHT_UNITS = ['g','kg','lb','oz']
VOLUME_UNITS = ['l','gal','oz','ml']
TEMP_UNITS = ['C','K','F']
RUBBISH_CONTENTS = ('used malt', 'used hops')
WORT_INGREDIENTS = {'liquid': ['water', 
                               'malt extract'
                               ],
                    'solid': ['malt',
                              'hops',
                          ]
                    }

class ContainerError(Exception):
    pass

class ContentType:
    Wort = 'wort'
    Hops = 'hops'
    Yeast = 'yeast'
    Water = 'water'
    Malt = 'malt'
    Beer = 'beer'
    

class Container(Document):
    name = TextField()
    container_type = TextField()
    size = DictField(Mapping.build(
        amount = DecimalField(),
        unit = TextField()
        ))

    contents = ListField(DictField(Mapping.build(
        amount = DecimalField(),
        unit = TextField(),
        content = TextField(),
        updated_datetime = DateTimeField(default=datetime.now),
        temperature = DictField(Mapping.build(
            degrees = DecimalField(),
            unit = TextField()
            )),
        content_type = TextField()
    )))
    full = BooleanField(default=False)

    def total_filled(self):
        """Return the amount of filled content. However, there is no weight to volume conversion. 
        E.g. weight is free in volume-organized container
        volume is free in weight-organized containers
        """
        total_amount = 0
        target_unit = self.size.unit
        for content in self.contents:
            if content.unit in VOLUME_UNITS and target_unit in WEIGHT_UNITS:
                continue
            converted_amount = convert_amount( (content.amount, content.unit), target_unit)
            total_amount += converted_amount

        return (total_amount, target_unit)

    def heat_contents(self, temp_tuple):
        """Set all the contents of the container to be a temperature of temp_tuple
        temp_tuple is (amount, units), e.g. (70, 'C')
        """

        if temp_tuple[1].upper() not in TEMP_UNITS:
            raise ContainerError("Unable to use the specified temperature unit %s" % (temp_tuple[1]))
        else:
            for content in self.contents:
                content.temperature = dict( degrees = temp_tuple[0],
                                         unit = temp_tuple[1].upper()
                )

    def set_size(self, size_tuple):
        if not ((size_tuple[1].lower() in WEIGHT_UNITS) or (size_tuple[1].lower() in VOLUME_UNITS)):
            raise ContainerError("Unable to use the specified unit: %s" % (size_tuple[1]))

        self.size = {'amount': size_tuple[0],
                         'unit': size_tuple[1].lower() }
    def determine_content_type(self, content):
        if "wort" in content.lower():
            return ContentType.Wort
        elif "hops" in content.lower():
            return ContentType.Hops
        elif "yeast" in content.lower():
            return ContentType.Yeast
        elif "malt" in content.lower():
            return ContentType.Malt
        elif "water" in content.lower():
            return ContentType.Water
        elif "beer" in content.lower():
            return ContentType.Beer

    def add_content(self, content, amount, temp = (23, "C"), content_type=None, updated_datetime=None):
        """
        :param amount - may be dictionary: {"amount": amount, "unit": unit}, or tuple (amount, unit)
        """
        if not updated_datetime:
            updated_datetime=datetime.now()
        LOGGER.info("Attempting to add content %s (amount %s, temp %s)", content, amount, temp)
        amount_dict = {}
        temp_dict = {}
        if not content_type:
            content_type = self.determine_content_type(content)
        
        if "unit" not in amount:
            amount_dict = {"amount": amount[0],
                        "unit": amount[1]}
        else:
            amount_dict = amount
        if amount_dict["unit"] != self.size.unit and amount_dict["unit"] in VOLUME_UNITS:
            raise ContainerError("Only able to add volume content measured in '{0}'".format(self.size.unit))
        
        #Assume room temperature
        if "unit" not in temp:
            temp_dict = {"degrees": 23,
                         "unit": "C"}
        else:
            temp_dict = temp
        if not amount_dict:
            raise ContainerError("Amount must be provided as (amount, unit) or as dictinoary ")

        # adding_amount is the value to add to the container
        adding_amount = amount_dict["amount"]
        if amount_dict["unit"] != self.size.unit:
            try:
                adding_amount = convert_amount(amount_dict, self.size.unit)
            except ContainerError as e:
                LOGGER.info("Unable to convert to unit %s. Not adding any volume. %s", self.size.unit, e)
                adding_amount = 0

        filled = self.total_filled()
        if float(filled[0]) + float(adding_amount) > self.size.amount:
            adding_amount = self.size.amount - filled[0]
            self.contents.append(
                dict( amount = adding_amount,
                      unit = self.size.unit,
                      content = content,
                      temperature = temp_dict,
                      content_type = content_type,
                      updated_datetime = updated_datetime,
                )
            )
            raise ContainerError("Error filling container: trying to add too much, only %s %s added (%s %s not added)" % (adding_amount, self.size.unit, amount_dict["amount"] - adding_amount, self.size.unit))
        LOGGER.info("Adding full content %s %s %s" % (content, amount_dict["amount"], amount_dict["unit"]))
        self.contents.append(
            dict( amount = amount_dict["amount"],
                  unit = amount_dict["unit"],
                  content = content,
                  temperature = temp_dict,
                  content_type = content_type,
                  updated_datetime = updated_datetime,
              ))

        if self.total_filled()[0] >= self.size.amount:
            self.full = True

        
    def remove_all(self):
        """Remove all contents, and return a list
        """
        removed = []
        for content in self.contents:
            removed.extend(self.remove_content(content.content, (content.amount, content.unit)))
            
        return removed

    def add_all(self, content_list):
        """content_list is a list of tuples ('content',(amount, unit), (degrees, unit))
        add the specified content to the list
        """
        LOGGER.info("Adding contents to container: %s", content_list)
        if not content_list:
            LOGGER.info("No contents to add")
            return
        for content in content_list:
            LOGGER.info("Attempting to add content %s", content)
            #for (content, amount_tuple, temperature_tuple) in content_list:

            try:
                self.add_content(content[0], content[1], content[2])
                LOGGER.info("Added content: %s", content)
            except IndexError:

                LOGGER.error("Unable to add content %s", content)

        
    def remove_content(self, content, amount_tuple):
        """Remove the specified amount of content
        :return a list of tuples of the removed contents (content, amount, temperature)
        """
        
        if content not in [ c.content for c in self.contents ]:
            raise ContainerError("Unable to remove the specify contents %s. The container is not currently filled with any")

        same_content = [ c for c in self.contents if c.content.lower() == content ]
        reducing_amount = amount_tuple[0]
        reducing_unit = amount_tuple[1]
        all_removed = []
        for current_content in self.contents:
            if current_content.content.lower() == content.lower():
                reducing_amount = convert_amount( (reducing_amount, reducing_unit), current_content.unit)
                LOGGER.info("Converted amount to remove: %s %s", reducing_amount, current_content.unit)
                if reducing_amount > current_content.amount:
                    LOGGER.info("Amount reduce %s %s more than current contained content %s %s", reducing_amount, current_content.unit, current_content.amount, current_content.unit)
                    reducing_amount = current_content.amount
                    content_tuple = (content,
                        (reducing_amount, current_content.unit),
                        (current_content.temperature.degrees, current_content.temperature.unit))
                    LOGGER.info("Removed content Appending content, amount, temperature %s to removed list %s", content_tuple,  all_removed)
                    # Reduce the total amount of content to be removed
                    reducing_amount -= current_content.amount

                    all_removed.append(content_tuple)
                    current_content.amount = 0
                else:
                    # Remove everything specified
                    LOGGER.info("Removing full specified amount %s %s", reducing_amount, current_content.unit)
                    current_content.amount -= reducing_amount
                    content_tuple = (content,
                                     {"amount": reducing_amount,
                                      "unit": current_content.unit},
                                     {"degrees": current_content.temperature.degrees,
                                      "unit": current_content.temperature.unit})
                    LOGGER.info("Updated content amount after reduction: %s %s", current_content.amount, current_content.unit)
                    #LOGGER.info("Removed list: appending content, amount, temperature %s to removed list %s", content_tuple,  all_removed)
                    LOGGER.info("Removed list addition: %s", content_tuple)
                    all_removed.append(content_tuple)
        LOGGER.info("List of all removed contents: %s", all_removed)
        # Remove the empty contents
        self.contents = [ c for c in self.contents if c.amount ]
        if self.total_filled()[0] < self.size.amount:
            self.full = False
        LOGGER.info("All removed content: %s", all_removed)
        return all_removed

class MashTun(Container):

    def __init__(self, size_tuple):
        super(MashTun, self).__init__(container_type='mash_tun')
        self.set_size(size_tuple)

    def convert_to_wort(self):
        """Convert the contents to wort.
        This replaces liquid contents with wort, and solid contents with 'used ...'
        :return a list of the previous contents
        """
        wort_contents = []
        total_wort_amount = {'amount': 0, 'unit': None}
        wort_temperature = {'degrees': None, 'unit': None}
        replaced_liquids = [] # liquids only
        all_replaced = [] # all OLD content
        new_contents = [] # all contents to be added again
        LOGGER.info("Type of contents: %s", type(self.contents))
        LOGGER.debug("Converting the following contents to wort: %s", self.contents)
        
        for content in self.contents:
            if content.content in WORT_INGREDIENTS['liquid']:
                if not total_wort_amount['amount']:
                    total_wort_amount['amount'] = content.amount
                    total_wort_amount['unit'] = content.unit
                    wort_temperature['degrees'] = content.temperature.degrees
                    wort_temperature['unit'] = content.temperature.unit
                else:
                    content_amount = convert_amount((content.amount, content.unit), total_wort_amount['unit'])
                    ratio = content_amount / total_wort_amount['amount']
                    content_temp = convert_temp((content.temperature.degrees, content.temperature.unit), wort_temperature['unit'])
                    if content_temp == wort_temperature['degrees']:
                        new_temperature = wort_temperature['degrees']
                    elif content_temp > wort_temperature['degrees']:
                        new_temperature = wort_temperature['degrees'] + ratio * content_temp
                    elif content_temp < wort_temperature['degrees']:
                        new_temperature = wort_temperature['degrees'] - ratio * content_temp
                    wort_temperature['degrees'] = new_temperature
                    total_wort_amount += convert_amount( (content.amount, content.unit), total_wort_amount['unit'])
                replaced_liquids.append(content)
                all_replaced.append(content)
                LOGGER.info("Tracking content %s for replacement"% content.content)
            elif content.content in WORT_INGREDIENTS['solid']:
                content.content = "used " + content.content
                all_replaced.append(content)
                LOGGER.info("Tracking content %s for replacement"% content.content)
        removed = []
        to_add = []
        wort_content = ("wort", total_wort_amount, wort_temperature)
        to_add += [ wort_content ]
        LOGGER.info("All content to be replaced: %s", [ c.content for c in all_replaced ])
        for content in all_replaced:
            LOGGER.info("Removing content: %s", content.content)
            removed.extend(self.remove_content(content.content, (content.amount, content.unit))) 

            if content.content in WORT_INGREDIENTS['solid'] or content.content.replace("used ","") in WORT_INGREDIENTS["solid"]:
                LOGGER.debug("Will 'add' back in solid ingredient %s", content.content)
                to_add.append( (content.content, 
                                {"amount": content.amount, "unit": content.unit}, 
                                {"degrees": content.temperature.degrees, "unit": content.temperature.unit}) )
            LOGGER.info("Updated list of temporarily 'removed' contents: %s", removed)            

        LOGGER.info("Adding replacement content in the container: %s", to_add)

        
        for content in to_add:
            LOGGER.info("Adding replacement content %s", content)
            LOGGER.info("Content: %s", content[0])
            LOGGER.info("Amount: %s", content[1])
            LOGGER.info("Temperature %s", content[2])
            self.add_content(content[0], content[1], content[2])

        return all_replaced
            
            
            
class FermentationError(Exception):
    pass

class PackagingError(Exception):
    pass

class Fermenter(Container):
    def __init__(self, size_tuple):
        super(Fermenter, self).__init__(container_type='fermenter')
        self.set_size(size_tuple)

    def into_kegs(self, kegs):
        """Move the beer content into kegs
        """
        beer_to_move = [ c for c in self.contents if c.content_type == c.ContentType.Beer ]

        if len(beer_to_move) != 1:
            raise PackagingError("Must have exactly one beer to transfer into kegs")
        beer = beer_to_move[0]
        total_remaining = {"amount": beer.amount, "unit": beer.unit }
        for keg in kegs:
            (amount, unit) = (keg.size.amount, keg.size.unit)
            # if unit != self.size.unit:
            #     raise PackagingError("Keg unit must be the same as container unit %s", self.size.unit)
            move_amount = convert_amount( (amount, unit), self.size.unit)
            removed = self.remove_content(beer.content, (move_amount, self.size.unit))
            
            for content in removed:
                keg.add_content(content[0], content[1], content[2], ContentType.Beer)
                total_remaining["amount"] -= convert_amount(content[1], beer.unit)
            if not total_remaining["amount"]
                LOGGER.info("No more volume to put into kegs")
                break
        if total_remaining:
            LOGGER.error("Insufficient kegs to package remaining beer: %s", total_remaining)
            raise PackagingError("Insufficient kegs to package remaining beer: %s" % total_remaining)

    def ferment_wort(self, timedelta):
        """Convert wort to beer, over the given timespan
        :return a list of the previous contents of the fermenter
        """
        if "wort" not in [ c.content for c in self.contents ]:
            raise FermentationError("No wort found in the fermenter, unable to ferment!")
        else:
            worts = [ c.content for c in self.contents if c.content == "wort" ]
        if len(worts) != 1:
            raise FermentationError("Unable to ferment multiple worts at one time: %s" % (worts))

        removed = []
        updated_datetime = None
        for content in self.contents:
            updated_datetime = content.updated_datetime+timedelta
            if content.content_type == ContentType.Wort:
                removed.extend(self.remove_content(content.content, (content.amount, content.unit)))
            
        to_add = []
        for (content, amount, temperature) in removed:
            self.add_content("beer", amount, temperature, ContentType.Beer, updated_datetime )

        return removed

class Storage(Container):
    def __init__(self, size_tuple):
        super(Storage, self).__init__(container_type='container')
        self.set_size(size_tuple)

class Keg(Container):
    def __init__(self, size_tuple):
        super(Keg, self).__init__(name, container_type='keg')
        self.set_size(size_tuple)

class Bottle(Container):
    def __init__(self, size_tuple):
        super(Bottle, self).__init__(name, container_type='bottle')
        self.set_size(size_tuple)

def convert_amount( amount, target_unit):
    """
    Convert the given amount into a target unit. Return a number (of the specified target_unit)
    """

    if "amount" in amount:
        amount_tuple = (amount["amount"], amount["unit"])
    else:
        amount_tuple = amount
    if amount_tuple[1] == target_unit:
        return amount_tuple[0]
    LOGGER.debug("Converting amount,unit %s into target unit %s", amount_tuple, target_unit)
    try:
        amount = amount_tuple[0]
        unit = amount_tuple[1]
    except IndexError as e:
        LOGGER.error("Unable to determine amount value based on (value, unit) %s: %s", amount_tuple, e)
        raise
        
    if unit == target_unit:
        return amount
    if target_unit == "l" and unit == "gal":
        return amount / 3.78541
    elif target_unit == "l" and unit == "ml":
        return amount / 1000
    elif target_unit == 'l' and unit == 'kg':
        # use 1 to 1 for kg to l
        return amount
    elif target_unit == 'l' and unit == 'g':
        if amount < 500:
            return 0
        else:
            return amount / 1000
    else:
        raise ContainerError("Unable to convert from %s into %s" % (unit, target_unit))


def move_all(first_container, second_container):
    """Move contents of first container into second container
    :return garbage unable to be removed
    :throw ContainerError if the amount cannot be fully input
    """
    
    removed = first_container.remove_all()
    LOGGER.info("Removed from the first container %s: %s", first_container.container_type, removed)
    to_add = [ content for content in removed if content not in RUBBISH_CONTENTS ]

    garbage = [ content for content in removed if content in RUBBISH_CONTENTS ]
    if garbage:
        LOGGER.info("Garbage from the moving process:", garbage)
    LOGGER.info("Items to add to second container %s: %s", second_container.container_type, to_add)
    second_container.add_all(to_add)
    LOGGER.info("Second container contents: %s", second_container.contents)
    return garbage
    
    
    
    
