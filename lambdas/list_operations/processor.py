from http import HTTPStatus
from logging import Logger
from typing import List

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService, ConditionType
from shared.models.operation_model import OperationOUT
from shared.pagination import Paginator
from shared.user_utils import get_user_id_from_cognito_authorizer


class ListOperationsProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_list_operations_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)

        params = event.get('queryStringParameters')
        if params is None or not params:
            params = {}
        self.logger.info(f"Processing list operations event for User: {user_id}",
                         extra={'QueryParameters': params})

        self.logger.info("Initializing paginator")
        page = params.get('page', '1')
        per_page = params.get('per_page', '10')
        paginator = Paginator(logger=self.logger,
                              page=page,
                              per_page=per_page)

        payload = self._evaluate_filter_conditions(params=params)

        self.logger.info("Sending query request to DynamoDB",
                         extra={'Payload': payload})
        operations_queryset: List[dict] = self.crud_service.list_items(**payload)
        operations_list = [OperationOUT(**record).dict() for record in operations_queryset]
        items = paginator.paginate(items_list=operations_list)
        response_body = {
            'page': int(page),
            'per_page': int(per_page),
            'total': paginator.total,
            'total_pages': paginator.total_pages,
            'data': items
        }
        return HTTPResponse(status_code=HTTPStatus.OK,
                            body=response_body)

    def _evaluate_filter_conditions(self, params: dict) -> dict:
        """
        Evaluates query parameters and modifies the query before sending to DynamoDB.
        :param params: Query parameters
        :return: crud_service.list_items method payload
        """
        self.logger.info("Evaluating filter conditions")
        payload = {
            'pk': f'Operation'
        }
        operation_type = params.get('operation_type')
        if operation_type:
            payload['gsi1'] = True
            payload['condition_type'] = ConditionType.BEGINS_WITH
            payload['condition_value'] = f'Operation#{operation_type.upper()}'
            return payload

        payload['condition_type'] = ConditionType.BEGINS_WITH
        payload['condition_value'] = 'Operation#'
        return payload
