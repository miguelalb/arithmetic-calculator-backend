from http import HTTPStatus
from logging import Logger
from typing import List

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService, ConditionType
from shared.date_utils import validate_date_epoch_string
from shared.error_handling import HTTPException
from shared.models.record_model import RecordOUT
from shared.pagination import Paginator
from shared.user_utils import get_user_id_from_cognito_authorizer


class ListRecordsProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_list_records_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)

        params = event.get('queryStringParameters')
        if params is None or not params:
            params = {}
        self.logger.info(f"Processing list records event for User: {user_id}",
                         extra={'QueryParameters': params})

        self.logger.info("Initializing paginator")
        page = params.get('page', '1')
        per_page = params.get('per_page', '10')
        paginator = Paginator(logger=self.logger,
                              page=page,
                              per_page=per_page)

        self.logger.info("Evaluating filter conditions")
        payload = self._evaluate_filter_conditions(user_id, params)

        self.logger.info("Sending query request to DynamoDB",
                         extra={'Payload': payload})
        records_queryset: List[dict] = self.crud_service.list_items(**payload)
        records_list = [RecordOUT(**record).dict() for record in records_queryset]
        items = paginator.paginate(items_list=records_list)
        response_body = {
            'page': int(page),
            'per_page': int(per_page),
            'total': paginator.total,
            'total_pages': paginator.total_pages,
            'data': items
        }
        return HTTPResponse(status_code=HTTPStatus.OK,
                            body=response_body)

    def _evaluate_filter_conditions(self, user_id: str, params: dict) -> dict:
        """
        Evaluates query parameters and modifies the query before sending to DynamoDB.
        :param user_id: User id from cognito authorizer
        :param params: Query parameters
        :return: crud_service.list_items method payload
        """
        payload = {
            'pk': f'User#{user_id}'
        }
        date_start = params.get('date_start')
        date_end = params.get('date_end')
        if date_start:
            payload = self._validate_and_get_records_after_equal_start_date(date_start=date_start,
                                                                            payload=payload)
            if date_end:
                payload = self._validate_and_get_records_between_start_and_end_date(date_start=date_start,
                                                                                    date_end=date_end,
                                                                                    payload=payload)
        elif date_end:
            payload = self._validate_and_get_records_before_equal_end_date(date_end=date_end,
                                                                           payload=payload)

        else:
            balance_start = params.get('balance_start')
            balance_end = params.get('balance_end')
            if balance_start:
                payload = self._validate_and_get_records_greater_than_equal_balance_start(balance_start=balance_start,
                                                                                          payload=payload)
                if balance_end:
                    payload = self._validate_and_get_records_between_balance_start_and_end(balance_start=balance_start,
                                                                                           balance_end=balance_end,
                                                                                           payload=payload)
            elif balance_end:
                payload = self._validate_and_get_records_less_than_equal_balance_end(balance_end=balance_end,
                                                                                     payload=payload)
            else:
                self.logger.info("No filters provided. Querying all user records.")
                payload['gsi1'] = True
                payload['gsi2'] = False
                payload['condition_type'] = ConditionType.BEGINS_WITH
                payload['condition_value'] = 'Record#'
        return payload

    def _validate_and_get_records_after_equal_start_date(self, date_start: str, payload: dict) -> dict:
        """
        Validate the date start parameter and modify payload to get records after the start date
        :param date_start: Start date to query from
        :param payload: crud_service.list_items method payload
        :return: updated payload
        """
        validate_date_epoch_string(logger=self.logger,
                                   date=date_start)
        payload['gsi1'] = True
        payload['condition_type'] = ConditionType.GREATER_THAN_OR_EQUAL
        payload['condition_value'] = f'Record#{date_start}'
        return payload

    def _validate_and_get_records_between_start_and_end_date(self,
                                                             date_start: str,
                                                             date_end: str,
                                                             payload: dict
                                                             ) -> dict:
        """
        Since both a date_start and date_end were provided, validate the date end parameter and
        modify the payload to get records between the start date an end date.
        :param date_start: Start date to query from
        :param date_end: End date to query until
        :param payload: crud_service.list_items method payload
        :return: updated payload
        """
        validate_date_epoch_string(logger=self.logger,
                                   date=date_end)
        self._validate_between_condition(start_value=date_start,
                                         end_value=date_end)
        payload.pop('condition_value')
        payload['condition_type'] = ConditionType.BETWEEN
        payload['low_value'] = f'Record#{date_start}'
        payload['high_value'] = f'Record#{date_end}'
        return payload

    def _validate_and_get_records_before_equal_end_date(self, date_end: str, payload: dict) -> dict:
        """
        Since only the date_end parameter was provided, validate the date end parameter and
        modify the payload to get records before the end date specified.
        :param date_end: End date to query until
        :param payload: crud_service.list_items method payload
        :return: modified payload
        """
        validate_date_epoch_string(logger=self.logger,
                                   date=date_end)
        payload['gsi1'] = True
        payload['condition_type'] = ConditionType.LESS_THAN_OR_EQUAL
        payload['condition_value'] = f'Record#{date_end}'
        return payload

    def _validate_and_get_records_greater_than_equal_balance_start(self, balance_start: str, payload: dict) -> dict:
        """
        Validate the user balance start parameter and modify the payload to get records greater or
        equal to the provided start balance.
        :param balance_start: The balance to query from
        :param payload: crud_service.list_items method payload
        :return: updated payload
        """
        self._validate_balance_parameter(balance=balance_start)
        payload['gsi2'] = True
        payload['condition_type'] = ConditionType.GREATER_THAN_OR_EQUAL
        payload['condition_value'] = f"Record#{balance_start}"
        return payload

    def _validate_and_get_records_between_balance_start_and_end(self,
                                                                balance_start: str,
                                                                balance_end: str,
                                                                payload: dict
                                                                ) -> dict:
        """
        Since both balance_start and balance_end were provided, validate the user balance end
        parameter and modify the payload to get records between balance start and balance end.
        :param balance_start: Balance to query the records from
        :param balance_end: Balance to query the records until
        :param payload: crud_service.list_items method payload
        :return: updated payload
        """
        self._validate_balance_parameter(balance=balance_end)
        self._validate_between_condition(start_value=balance_start,
                                         end_value=balance_end)
        payload.pop('condition_value')
        payload['condition_type'] = ConditionType.BETWEEN
        payload['low_value'] = f'Record#{balance_start}'
        payload['high_value'] = f'Record#{balance_end}'
        return payload

    def _validate_and_get_records_less_than_equal_balance_end(self, balance_end: str, payload: dict) -> dict:
        """
        Since only the balance_end was provided, validate the balance_end parameter and
        modify the payload to get the records less than or equal to the provided balance
        :param balance_end: Balance to query records until
        :param payload: crud_service.list_items method payload
        :return: updated payload
        """
        self._validate_balance_parameter(balance=balance_end)
        payload['gsi2'] = True
        payload['condition_type'] = ConditionType.LESS_THAN_OR_EQUAL
        payload['condition_value'] = f'Record#{balance_end}'
        return payload

    def _validate_balance_parameter(self, balance: str) -> None:
        """
        Validate the balance parameter
        :param balance: Balance to validate
        """
        if not balance.isnumeric():
            self.logger.error(f"Balance value is not numeric {balance}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Balance value must be numeric")

        if int(balance) < 0:
            self.logger.error(f"Negative balance value {balance}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Negative balance not allowed")

    def _validate_between_condition(self, start_value: str, end_value: str) -> None:
        """
        Validate parameters in a between condition
        :param start_value: The initial value ot evaluate
        :param end_value: The end value to evaluate
        """
        if int(start_value) > int(end_value):
            self.logger.error(f"Start value {start_value} greater than end value {end_value}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Start value cannot be greater than end value.")

