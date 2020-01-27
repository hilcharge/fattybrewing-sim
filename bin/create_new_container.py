"""A script to create a new container as part of the brewing simulation
"""

import os
import sys
import getopt

import re

import logging

sys.path.append(os.path.dirname(__file__),"..","lib")

from fattybrewing import container

CONTAINER_TYPES = ("mash_tun", "fermenter", "storage", "keg", "bottle")
UNITS = ("gal","l","kg","g","lb", "ml", "oz")

def usage():
    usage_str = """
{} [OPTIONS] -t CONTAINER_TYPE -s SIZE

CONTAINER_TYPE - one of mash_tun, fermenter, storage, keg, bottle
SIZE - must be of format NUMBER+UNIT, e.g. 35Gal, 20L, 10kg

""".format(sys.argv[0])


def generate_new_contaier(container_type, size):
    """Return a new container object
"""
    
    new_container = None
    if container_type == "mash_tun":
        new_container = container.MashTun(size)

    elif container_type == "fermenter":
        new_container = container.Fermenter(size)

    elif container_type == "storage":
        new_container = container.Storage(size)
        
    elif container_type == "keg":
        new_container = container.Keg(size)
        
    elif container_type == "bottle":
        new_container = container.Bottle(size)

    else:
        raise Exception("Unknown container type: {}".format(container_type))

    return new_container

def main():

    args = sys.argv[1:]
    container_type = None
    size = None ## Size is a tuplet of (number, unit)

    try: 
        opts, args = getopt.getopt(args, "hs:t:", ["size=", "container-type=", "help"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--container-type"):
            if a not in CONTAINER_TYPES:
                raise Exception("Container type must be one of %s" % (CONTAINER_TYPES))
            container_type = a
        elif o in ("-s", "--size"):
            match = re.match(r'^([\d\.]+)([\w]+)$', a)
            size = (match.group(1), match.group(2))
            if size[1].lower() not in UNITS:
                raise Exception("Units must be one of %s" % (UNITS))
            if not (size[0] and size[1]):
                raise Exception("Size must be provided as NUMBER+UNITS (e.g. 25L, 10gal, 5g, 20kg)")
            
    new_container = None

    new_container = generate_new_container(container_type, size)
    print("Saving new container: {}".format(new_container))
    new_container.save()

            
if __name__ == "__main__":
    main()
