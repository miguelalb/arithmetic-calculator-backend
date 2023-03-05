import pytest
from boto3.dynamodb.conditions import Key, Attr
from mock import MagicMock

from shared.crud_service import ConditionType, CrudService
from shared.fixture_utils import json_fixture
from shared.models.operation_model import OperationIN

mock_logger = MagicMock()
mock_table = MagicMock()

CRUD_SERVICE_SAMPLE_DATA_ITEM = json_fixture('crud_service_sample_data_item.json')


@pytest.fixture()
def crud_service():
    return CrudService(logger=mock_logger,
                       table=mock_table)


def test_crud_service_create_success(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    operation_in_dict = operation_in.dict()

    crud_service.create(operation_in_dict)
    expected = {
        'Item': operation_in_dict,
        'ConditionExpression': Attr('PK').not_exists() & Attr('SK').not_exists()
    }

    mock_table.put_item.assert_called_with(**expected)


def test_crud_service_update_success(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    operation_in_dict = operation_in.dict()

    crud_service.update(operation_in_dict)
    expected = {
        'Item': operation_in_dict,
        'ConditionExpression': Attr('PK').exists() & Attr('SK').exists()
    }

    mock_table.put_item.assert_called_with(**expected)


def test_crud_service_update_item_attributes_success(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    pk = operation_in.PK
    sk = operation_in.SK
    update_expression = 'SET #cost = :cost'
    expression_attribute_names = {'#cost': 'cost'}
    expression_attribute_values = {':cost': 2}

    crud_service.update_item_attributes(pk=pk,
                                        sk=sk,
                                        update_expression=update_expression,
                                        expression_attribute_names=expression_attribute_names,
                                        expression_attribute_values=expression_attribute_values)

    expected = {
        'Key': {'PK': pk, 'SK': sk},
        'UpdateExpression': update_expression,
        'ExpressionAttributeNames': expression_attribute_names,
        'ExpressionAttributeValues': expression_attribute_values,
        'ConditionExpression': Attr('PK').exists() & Attr('SK').exists(),
        'ReturnValues': 'ALL_NEW'
    }

    mock_table.update_item.assert_called_with(**expected)


def test_crud_service_get_success(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    pk = operation_in.PK
    sk = operation_in.SK

    crud_service.get(pk=pk,
                     sk=sk)

    expected = {
        'Key': {'PK': pk, 'SK': sk}
    }

    mock_table.get_item.assert_called_with(**expected)


def test_crud_service_delete_success(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    pk = operation_in.PK
    sk = operation_in.SK

    crud_service.delete(pk=pk,
                        sk=sk)

    expected = {
        'Key': {'PK': pk, 'SK': sk},
        'ReturnValues': 'ALL_OLD'
    }

    mock_table.delete_item.assert_called_with(**expected)


def test_crud_service_list_items_partition_key_only(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    pk = operation_in.PK

    crud_service.list_items(pk=pk)

    expected = {
        'KeyConditionExpression': Key('PK').eq(pk)
    }

    mock_table.query.assert_called_with(**expected)


def test_crud_service_list_items_by_global_secondary_index(crud_service):
    data = CRUD_SERVICE_SAMPLE_DATA_ITEM
    operation_in = OperationIN(**data)
    pk = operation_in.GSI1PK
    condition_type = ConditionType.BEGINS_WITH
    condition_value = 'Operation#type'

    crud_service.list_items(pk=pk,
                            gsi1=True,
                            condition_type=condition_type,
                            condition_value=condition_value)

    expected = {
        'IndexName': 'GSI1',
        'KeyConditionExpression': Key('GSI1PK').eq(pk) & Key('GSI1SK').begins_with(condition_value)
    }

    mock_table.query.assert_called_with(**expected)
