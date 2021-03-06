# Note: The schema is stored in a .py file in order to take advantage of the
# int() and float() type coercion functions. Otherwise it could easily stored as
# as JSON or another serialized format.
"""
This file is adapted from the Lesson 4 Section 13 of Data Analyst Program
"""
schema = {
    'node': {
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'key': {'required': True, 'type': 'string'},
            'value': {'required': True, 'type': 'string'},
            'type': {'required': True, 'type': 'string'}
        }
    },
    'way': {
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'node_id': {'required': True, 'type': 'integer', 'coerce': int},
            'position': {'required': True, 'type': 'integer', 'coerce': int}
        }
    },
    'way_tags': {
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'key': {'required': True, 'type': 'string'},
            'value': {'required': True, 'type': 'string'},
            'type': {'required': True, 'type': 'string'}
        }
    }
}
