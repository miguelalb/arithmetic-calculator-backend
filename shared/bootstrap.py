
"""
Bootstrap scripts to run on the first request after initial deployment.
"""
from logging import Logger

from shared.crud_service import CrudService, ConditionType
from shared.models.operation_model import OperationIN, OperationType


def create_operations_if_not_exists(logger: Logger, crud_service: CrudService):
    operation_check = crud_service.list_items(pk='Operation',
                                              condition_type=ConditionType.BEGINS_WITH,
                                              condition_value='Operation')
    if not operation_check:
        logger.info("Creating Operations in DB.")
        cost = 1
        for operation_type in OperationType:
            operation_in = OperationIN(type=operation_type,
                                       cost=cost)
            crud_service.create(item=operation_in.dict())
            cost += 1
