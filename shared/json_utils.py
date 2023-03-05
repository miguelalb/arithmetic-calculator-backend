from uuid import UUID

import simplejson as json

"""
Helper functions/classes for JSON serialization and deserialization
"""


def json_str_to_dict(data: str) -> dict:
    """
    Deserializes a json str to a dictionary object
    :param data: json str to  serialize
    :return: serialized dictionary object
    """
    return json.loads(data, encoding='utf-8')


def dict_to_json_str(data: dict) -> str:
    """
    Serializes from a dictionary object to a json string.
    :param data: Dictionary object to serialize
    :return: json str
    """
    return json.dumps(data, encoding='utf-8', cls=CustomSerializer)


class CustomSerializer(json.JSONEncoder):
    """
    Custom logic to serialize complex objects.
    """

    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, return the str value of uuid
            return str(obj)

        return json.JSONEncoder.default(self, obj)
