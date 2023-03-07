from http import HTTPStatus
from logging import Logger

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService
from shared.models.record_model import RecordOUT, DEFAULT_INITIAL_USER_BALANCE
from shared.record_utils import is_user_first_operation, get_user_most_recent_record
from shared.user_utils import get_user_id_from_cognito_authorizer


class GetBalanceEventProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_get_balance_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)

        self.logger.info(f"Processing Get Balance request for User {user_id}")

        user_records_db = get_user_most_recent_record(crud_service=self.crud_service,
                                                      user_id=user_id)

        if is_user_first_operation(logger=self.logger,
                                   user_records_db=user_records_db):
            self.logger.info(f"User first operation, default initial balance: {DEFAULT_INITIAL_USER_BALANCE}")
            return HTTPResponse(status_code=HTTPStatus.OK,
                                body={'UserId': user_id, 'UserBalance': DEFAULT_INITIAL_USER_BALANCE})

        user_record = RecordOUT(**user_records_db[0])
        self.logger.info(f"Returning current balance: {user_record.user_balance} for User: {user_id}")
        return HTTPResponse(status_code=HTTPStatus.OK,
                            body={'UserId': user_id, 'UserBalance': user_record.user_balance})
