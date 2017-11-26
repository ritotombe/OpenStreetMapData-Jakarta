#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""
This file is adapted from the Lesson 4 Section 13 of Data Analyst Program
"""
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import schema

OSM_PATH = "jakarta_indonesia.osm"

NODES_PATH = "files/nodes.csv"
NODE_TAGS_PATH = "files/nodes_tags.csv"
WAYS_PATH = "files/ways.csv"
WAY_NODES_PATH = "files/ways_nodes.csv"
WAY_TAGS_PATH = "files/ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[()\-\=\+/&<>;\'\"\?%#$@\,\.\ \t\r\n]')

ADDRESS_ABBRV = re.compile(r'(j|J)(l|ln|I|L|LN)(\s|\.)|jalan')
POSTAL_CODE = re.compile(r'[0-9]{5}')
CITY = re.compile(r'(Bekasi|bekasi|Jakarta|jakarta|Tangerang|tangerang|Bogor|bogor|Depok|depok|Banten|banten)|((Bekasi|bekasi|Jakarta|jakarta|Tangerang|tangerang|Bogor|bogor|Depok|depok|Banten|banten)\s[a-zA-Z]+)|([a-zA-Z]+\s(Banten|banten|Bekasi|bekasi|Jakarta|jakarta|Tangerang|tangerang|Bogor|bogor|Depok|depok))')
PHONE_PROBLEMCHARS = re.compile(r'')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

CITY_TRANSLATION = {
    "south jakarta": "Jakarta Selatan",
    "north jakarta": "Jakarta Utara",
    "west jakarta": "Jakarta Barat",
    "east jakarta": "Jakarta Timur",
    "central jakarta": "Jakarta Pusat"
}

""" START Data Cleaning Functions """

def fix_address(data):
    data = ADDRESS_ABBRV.sub('Jalan ', data)
    data = data.replace("  ", " ") #delete double spaces
    data = data.encode('ascii', 'ignore').decode() #remove unicode characters
    if 'Jalan' not in data:
        data = "Jalan "+ data
    for value in re.split(',\s|,', data):
        if "Jalan" in value:
            data = value
    return data

def fix_postal(data):
    if len(POSTAL_CODE.findall(data)) > 0:
        return POSTAL_CODE.findall(data)[0]
    else:
        return '00000'

def fix_language(data):
    if CITY.fullmatch(data) is not None:
        data = CITY.fullmatch(data)[0]
        if data.lower() in CITY_TRANSLATION:
            data = CITY_TRANSLATION[data.lower()]
    return data

def fix_phone(data):
    data = PROBLEMCHARS.sub("", data)
    return data

""" END Data Cleaning Functions """

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        # Handle node
        for data in NODE_FIELDS:
            node_attribs[data] = element.attrib[data]

    elif element.tag == 'way':
        # Handle way
        for data in WAY_FIELDS:
            way_attribs[data] = element.attrib[data]
        node_num = 0
        way_node = {}
        # Handle way nodes
        for way_node_el in element.findall('nd'):
            way_node = {
                'id': element.attrib['id'],
                'node_id': way_node_el.attrib['ref'],
                'position': node_num,
            }
            node_num += 1
            way_nodes.append(way_node)

    # Handle tags
    for tags_data in element.findall('tag'):
        info = {}
        for tags_field in NODE_TAGS_FIELDS:
            if tags_field == "key":
                if LOWER_COLON.match(tags_data.attrib["k"]):
                    splitted = tags_data.attrib["k"].split(":")
                    if  len(splitted) == 2:
                        info["type"], info["key"] = splitted
                    else:
                        info["type"], info["key"] = splitted[0], splitted[1:]

                    if info["key"] == "street":
                        fix_address(tags_data.attrib["v"])
                else:
                    info["key"] = tags_data.attrib["k"]
                    info["type"] = 'regular'
            elif tags_field == "id":
                info[tags_field] = element.attrib[tags_field]
            elif tags_field == "value":
                fixed = tags_data.attrib["v"]
                if info["key"] == "street":
                    fixed = fix_address(tags_data.attrib["v"])
                if info["key"] == "postcode":
                    fixed = fix_postal(tags_data.attrib["v"])
                if info["key"] == "city":
                    fixed = fix_language(tags_data.attrib["v"])
                if info["key"] == "phone":
                    fixed = fix_phone(tags_data.attrib["v"])
                info[tags_field] = fixed

            tags.append(info)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}



# ================================================== #
#               Helper Functions  (From UDACITY)                    #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function          (Adapted From Udacity)              #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        cnt=0
        for element in get_element(file_in, tags=('node', 'way')):
            # Number of element used
            cnt += 1
            print (cnt)
            # if cnt > 5000000:
            #     break
            el = shape_element(element)
            if el:
                # if validate is True:
                #     validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)
