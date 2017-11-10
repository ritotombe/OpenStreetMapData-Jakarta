#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""
After auditing is complete the next step is to prepare the data to be inserted into a SQL database.
To do so you will parse the elements in the OSM XML file, transforming them from document format to
tabular format, thus making it possible to write to .csv files.  These csv files can then easily be
imported to a SQL database as tables.

The process for this transformation is as follows:
- Use iterparse to iteratively step through each top level element in the XML
- Shape each element into several data structures using a custom function
- Utilize a schema and validation library to ensure the transformed data is in the correct format
- Write each data structure to the appropriate .csv files

We've already provided the code needed to load the data, perform iterative parsing and write the
output to csv files. Your task is to complete the shape_element function that will transform each
element into the correct format. To make this process easier we've already defined a schema (see
the schema.py file in the last code tab) for the .csv files and the eventual tables. Using the
cerberus library we can validate the output against this schema to ensure it is correct.

## Shape Element Function
The function should take as input an iterparse Element object and return a dictionary.

### If the element top level tag is "node":
The dictionary returned should have the format {"node": .., "node_tags": ...}

The "node" field should hold a dictionary of the following top level node attributes:
- id
- user
- uid
- version
- lat
- lon
- timestamp
- changeset
All other attributes can be ignored

The "node_tags" field should hold a list of dictionaries, one per secondary tag. Secondary tags are
child tags of node which have the tag name/type: "tag". Each dictionary should have the following
fields from the secondary tag attributes:
- id: the top level node id attribute value
- key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
- value: the tag "v" attribute value
- type: either the characters before the colon in the tag "k" value or "regular" if a colon
        is not present.

Additionally,

- if the tag "k" value contains problematic characters, the tag should be ignored
- if the tag "k" value contains a ":" the characters before the ":" should be set as the tag type
  and characters after the ":" should be set as the tag key
- if there are additional ":" in the "k" value they and they should be ignored and kept as part of
  the tag key. For example:

  <tag k="addr:street:name" v="Lincoln"/>
  should be turned into
  {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}

- If a node has no secondary tags then the "node_tags" field should just contain an empty list.

The final return value for a "node" element should look something like:

{'node': {'id': 757860928,
          'user': 'uboot',
          'uid': 26299,
       'version': '2',
          'lat': 41.9747374,
          'lon': -87.6920102,
          'timestamp': '2010-07-22T16:16:51Z',
      'changeset': 5288876},
 'node_tags': [{'id': 757860928,
                'key': 'amenity',
                'value': 'fast_food',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'cuisine',
                'value': 'sausage',
                'type': 'regular'},
               {'id': 757860928,
                'key': 'name',
                'value': "Shelly's Tasty Freeze",
                'type': 'regular'}]}

### If the element top level tag is "way":
The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}

The "way" field should hold a dictionary of the following top level way attributes:
- id
- user
- uid
- version
- timestamp
- changeset

All other attributes can be ignored

The "way_tags" field should again hold a list of dictionaries, following the exact same rules as
for "node_tags".

Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
dictionaries, one for each nd child tag.  Each dictionary should have the fields:
- id: the top level element (way) id
- node_id: the ref attribute value of the nd tag
- position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
            the way element

The final return value for a "way" element should look something like:

{'way': {'id': 209809850,
         'user': 'chicago-buildings',
         'uid': 674454,
         'version': '1',
         'timestamp': '2013-03-13T15:58:04Z',
         'changeset': 15353317},
 'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
               {'id': 209809850, 'node_id': 2199822390, 'position': 1},
               {'id': 209809850, 'node_id': 2199822392, 'position': 2},
               {'id': 209809850, 'node_id': 2199822369, 'position': 3},
               {'id': 209809850, 'node_id': 2199822370, 'position': 4},
               {'id': 209809850, 'node_id': 2199822284, 'position': 5},
               {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
 'way_tags': [{'id': 209809850,
               'key': 'housenumber',
               'type': 'addr',
               'value': '1412'},
              {'id': 209809850,
               'key': 'street',
               'type': 'addr',
               'value': 'West Lexington St.'},
              {'id': 209809850,
               'key': 'street:name',
               'type': 'addr',
               'value': 'Lexington'},
              {'id': '209809850',
               'key': 'street:prefix',
               'type': 'addr',
               'value': 'West'},
              {'id': 209809850,
               'key': 'street:type',
               'type': 'addr',
               'value': 'Street'},
              {'id': 209809850,
               'key': 'building',
               'type': 'regular',
               'value': 'yes'},
              {'id': 209809850,
               'key': 'levels',
               'type': 'building',
               'value': '1'},
              {'id': 209809850,
               'key': 'building_id',
               'type': 'chicago',
               'value': '366409'}]}
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
}

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
#               Helper Functions                     #
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
#               Main Function                        #
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
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
