from pydantic import BaseModel

from shared.json_utils import dict_to_json_string


class Base(BaseModel):
    """
    Base model to add common shared additional functionality
    """

    def to_string(self):
        """
        Serializes to a json string
        :return: Json string
        """
        return dict_to_json_string(self.dict())
