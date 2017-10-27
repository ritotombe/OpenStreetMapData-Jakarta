#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

import sys


OSMFILE = "jakarta_indonesia.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# expected = ["JL", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
#             "Trail", "Parkway", "Commons"]
#
# # UPDATE THIS VARIABLE
# mapping = { "St": "Street",
#             "St.": "Street",
#             "Ave": "Avenue",
#             "Rd.": "Road"
#             }

"""
errors
- b'\xc3\xa2\xc2\x80\xc2\x8eJl. Ir. H. Djuanda No. 95'
- b'JI.Margonda Raya No. 428, Beji, Depok , Indonesia'
- b'M.I. RIDWAN RAIS NO. 37, Beji Timur. Depok'
- b'Sentra Niaga Puri Indah'

'Pamulang Permai blok D III no. 1-2',
'22',

'10310',
'14450.',


- 'Jakarta Selatan',
- 'South Jakarta',

{'k': 'name', 'v': 'SMAN 7 Bogor'}
{'k': 'amenity', 'v': 'school'}
{'k': 'jenjang', 'v': 'SMA'}
{'k': 'alt_name', 'v': 'sman7bogor'}
{'k': 'addr:street', 'v': 'Jl. Palupuh Bantarjati No.7'}
{'k': 'addr:housename', 'v': 'SMA Negeri 7 Bogor'}
{'k': 'addr:housenumber', 'v': '0251-8326739'}


"""
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

result={}

'''
Check all possible tags and its value, only select with address to indicate it is a location
'''
def audit(osmfile):

    osm_file = open(osmfile, "r",  encoding='latin1')
    street_types = defaultdict(set)
    cnt=0

    for event, elem in ET.iterparse(osm_file, events=("start",)):
        cnt += 1
        if cnt == 5000000:
            break
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):

                    # all_descendants = list(elem.iter())
                    for data in elem.iter("tag"):
                        # pprint.pprint(data.attrib['k'])
                        if data.attrib["k"] not in result:
                            result[data.attrib["k"]]=[]
                            result[data.attrib["k"]].append(data.attrib["v"])
                        else:
                            result[data.attrib["k"]].append(data.attrib["v"])
                    break
                    # audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    test = str(result).encode('utf8')
    sys.stdout.buffer.write(test)
    return street_types


def update_name(name, mapping):

    found = street_type_re.search(name).group()


    return name.replace(found, mapping[found])


def test():
    st_types = audit(OSMFILE)
    # assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    # for st_type, ways in st_types.iteritems():
    #     for name in ways:
    #         better_name = update_name(name, mapping)
    #         print name, "=>", better_name
    #         if name == "West Lexington St.":
    #             assert better_name == "West Lexington Street"
    #         if name == "Baldwin Rd.":
    #             assert better_name == "Baldwin Road"


if __name__ == '__main__':

    test()
