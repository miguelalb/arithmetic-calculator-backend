from enum import Enum
from http import HTTPStatus
from logging import Logger
from typing import Optional, Any

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from shared.error_handling import HTTPException


class ConditionType(str, Enum):
    EQUALS = 'eq'
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUAL = 'lte'
    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUAL = 'gte'
    BEGINS_WITH = 'begins_with'
    BETWEEN = 'between'


class CrudService:
    """
    Encapsulates DynamoDB crud operations including error handling.
    Reference/examples: https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/dynamodb
    """

    def __init__(self,
                 logger: Logger,
                 table
                 ) -> None:
        self.logger = logger
        self.table = table

    def create(self, item: dict) -> None:
        """
        Create/Save an item
        :param item: Item to create
        :return: None
        """
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('PK').not_exists() & Attr('SK').not_exists()
            )
        except ClientError as err:
            self.logger.exception(
                "Exception on Put operation for a new item.",
                extra={
                    'Item': item,  # Fine for this app, but potential sensitive data shouldn't be logged in prod
                    'Exception': err
                }
            )
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Oops. Something went wrong when trying to add the item to the DB.")

    def update(self, item: dict) -> None:
        """
        Update an existing item.
        This operation uses the put_item method and replaces the original item with the updated version.
        :param item: Item to update
        :return: None
        """
        try:
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('PK').exists() & Attr('SK').exists()
            )
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.exception(
                    "Item does not exist.",
                    extra={'Exception': err}
                )
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    msg="Item does not exits.")
            else:
                self.logger.exception(
                    "Exception on Item update.",
                    extra={
                        'Item': item,
                        'Exception': err
                    }
                )
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    msg="Oops. Something went wrong when trying to Update item.")

    def update_item_attributes(self, pk: str, sk: str, update_expression: str,
                               expression_attribute_names: dict, expression_attribute_values: dict = None
                               ) -> Optional[dict]:
        """
        Updates an item's attributes.
        This operation uses the update_item method and only updates the attributes requested.
        :param pk: Primary key
        :param sk: Sort Key
        :param update_expression: DynamoDB update expression
        :param expression_attribute_names: Attributes to update
        :param expression_attribute_values: Attribute values
        :return: Updated item or None
        """
        try:
            if expression_attribute_values:
                response = self.table.update_item(
                    Key={'PK': pk, 'SK': sk},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ConditionExpression=Attr('PK').exists() & Attr('SK').exists(),
                    ReturnValues='ALL_NEW'
                )
                return response.get('Attributes', None)

            response = self.table.update_item(
                Key={'PK': pk, 'SK': sk},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ConditionExpression=Attr('PK').exists() & Attr('SK').exists(),
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes', None)
        except ClientError as err:
            if err.response['Error']['Code'] == 'ConditionalCheckFailedException':
                self.logger.exception(
                    f"Item does not exist. pk: {pk}, sk: {sk}",
                    extra={'Exception': err}
                )
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                    msg='Item does not exists')
            else:
                self.logger.exception(
                    f"Could not update item {expression_attribute_values}",
                    extra={'Exception': err}
                )
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                    msg='Oops. Something went wrong when trying to update Item attributes.')

    def get(self, pk: str, sk: str = '') -> Optional[dict]:
        """
        Get item by Primary Key.
        :param pk: Primary key
        :param sk: [Optional] Sort Key
        :return: Item or None
        """
        try:
            key = {'PK': pk}
            if sk:
                key['SK'] = sk
            response = self.table.get_item(Key=key)
            return response.get('Item', None)
        except ClientError as err:
            self.logger.exception(
                f"Could not get item. PK: {pk}, SK: {sk}",
                extra={'Exception': err}
            )
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Item does not exists.")

    def delete(self, pk: str, sk: str) -> Optional[dict]:
        """
        Delete an item
        :param pk: Primary key
        :param sk: Sort key
        :return: Old item or None
        """
        try:
            response = self.table.delete_item(Key={'PK': pk, 'SK': sk},
                                              ReturnValues='ALL_OLD')
            return response.get('Attributes', None)
        except ClientError as err:
            self.logger.exception(
                f"Could not delete item. PK: {pk}, SK: {sk}",
                extra={'Exception': err}
            )
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Item does not exists.")

    def list_items(self,
                   pk: str,
                   gsi1: bool = False,
                   gsi2: bool = False,
                   condition_type: ConditionType = '',
                   condition_value: Any = None,
                   low_value: Any = None,
                   high_value: Any = None,
                   ascending: bool = False,
                   limit: int = 9999
                   ) -> Optional[list]:
        """
        Generic table query abstraction to list items.
        :param pk: Primary key
        :param gsi1: Query on GSI1 index
        :param gsi2: Query on GSI2 index
        :param condition_type: Sort key condition to satisfy values
        :param condition_value: Condition value
        :param low_value: Low value to use in Between condition type
        :param high_value: High value to use in Between condition type
        :param ascending: Controls the ScanIndexForward parameter
        :param limit: Limit the amount of records
        :return:
        """
        try:
            partition_key = 'PK'
            sort_key = 'SK'
            index_name = ''

            if gsi1:
                partition_key = 'GSI1PK'
                sort_key = 'GSI1SK'
                index_name = 'GSI1'
            if gsi2:
                partition_key = 'GSI2PK'
                sort_key = 'GSI2SK'
                index_name = 'GSI2'

            if condition_type:
                condition_expression = self._get_sort_key_condition_expression(sort_key=sort_key,
                                                                               condition=condition_type,
                                                                               condition_value=condition_value,
                                                                               low_value=low_value,
                                                                               high_value=high_value)
                if index_name:
                    response = self.table.query(
                        IndexName=index_name,
                        ScanIndexForward=ascending,
                        Limit=limit,
                        KeyConditionExpression=Key(partition_key).eq(pk) & condition_expression)
                else:
                    response = self.table.query(
                        ScanIndexForward=ascending,
                        Limit=limit,
                        KeyConditionExpression=Key(partition_key).eq(pk) & condition_expression)

                return response['Items']

            if index_name:
                response = self.table.query(IndexName=index_name,
                                            ScanIndexForward=ascending,
                                            Limit=limit,
                                            KeyConditionExpression=Key(partition_key).eq(pk))
            else:
                response = self.table.query(ScanIndexForward=ascending,
                                            Limit=limit,
                                            KeyConditionExpression=Key(partition_key).eq(pk))

            return response['Items']

        except ClientError as err:
            query_input_values = {
                'pk': pk,
                'condition': condition_type,
                'condition_value': condition_value,
                'low_value': low_value,
                'high_value': high_value
            }
            self.logger.exception(
                f"Could not process query with input values: {query_input_values}",
                extra={'Exceptions': err})
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Oops. Something went wrong when trying to list items.")

    def _get_sort_key_condition_expression(self,
                                           sort_key: str,
                                           condition: ConditionType,
                                           condition_value: Any,
                                           low_value: Any = None,
                                           high_value: Any = None
                                           ) -> dict:
        self.logger.info(
            f"Query with condition: {condition} and value: {condition_value} on sort key: {sort_key}")
        condition_map = {
            ConditionType.EQUALS: Key(sort_key).eq(condition_value),
            ConditionType.LESS_THAN: Key(sort_key).lt(condition_value),
            ConditionType.LESS_THAN_OR_EQUAL: Key(sort_key).lte(condition_value),
            ConditionType.GREATER_THAN: Key(sort_key).gt(condition_value),
            ConditionType.GREATER_THAN_OR_EQUAL: Key(sort_key).gte(condition_value),
            ConditionType.BEGINS_WITH: Key(sort_key).begins_with(condition_value),
            ConditionType.BETWEEN: Key(sort_key).between(low_value, high_value)
        }
        return condition_map.get(condition)
