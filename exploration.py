#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import sys

OSMFILE = "jakarta_indonesia.osm"
STREET_TYPE_RE = re.compile(r'\b\S+\.?$', re.IGNORECASE)
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')

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
        # Number of line to be processed
        if cnt == 2000000:
            break
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                    '''
                    Uncomment for results
                    '''
                # # General data
                #     for data in elem.iter("tag"):
                #         # pprint.pprint(data.attrib['k'])
                #         if data.attrib["k"] not in result:
                #             result[data.attrib["k"]]=[]
                #             result[data.attrib["k"]].append(data.attrib["v"])
                #         else:
                #             result[data.attrib["k"]].append(data.attrib["v"])
                #     break
                # # end General data

                # # Contact
                #     for data in elem.iter("tag"):
                #         if LOWER_COLON.match(data.attrib["k"]):
                #             types, key = data.attrib["k"].split(":")
                #             if 'contact' in types:
                #                 if key not in result:
                #                     result[key] = 0
                #                     result[key] += 1
                #                 else:
                #                     result[key] += 1
                #     break
                # # end Contact

                # # Phone
                #     for data in elem.iter("tag"):
                #         if 'phone' in data.attrib["k"]:
                #             if data.attrib["k"] not in result:
                #                 result[data.attrib["k"]] =[]
                #                 result[data.attrib["k"]].append(data.attrib["v"])
                #             else:
                #                 result[data.attrib["k"]].append(data.attrib["v"])
                #     break
                # # end Phone

                # # Post Code
                #     for data in elem.iter("tag"):
                #         if 'postcode' in data.attrib["k"]:
                #             if len(data.attrib["v"]) not in result:
                #                 result[len(data.attrib["v"])] = 0
                #                 result[len(data.attrib["v"])] += 1
                #             else:
                #                 result[len(data.attrib["v"])] += 1
                #             if len(data.attrib["v"]) > 5:
                #                 print(data.attrib["v"].encode('utf8'))
                #     break
                # # end Post Code

                # # City
                #     for data in elem.iter("tag"):
                #         if ':city' in data.attrib["k"]:
                #
                #             if data.attrib["v"] not in result:
                #                 result[data.attrib["v"]] = 0
                #                 result[data.attrib["v"]] += 1
                #             else:
                #                 result[data.attrib["v"]] += 1
                #     break
                # # end City




    osm_file.close()
    return result

def test():
    data = audit(OSMFILE)
    # assert len(st_types) == 3
    pprint.pprint(dict(data))


if __name__ == '__main__':

    test()
