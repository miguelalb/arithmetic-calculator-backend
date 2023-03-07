from http import HTTPStatus
from logging import Logger

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService
from shared.error_handling import HTTPException
from shared.models.record_model import RecordOUT
from shared.user_utils import get_user_id_from_cognito_authorizer


class PollResultsProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_poll_results_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)
        record_id = event.get('pathParameters', {}).get('record_id', '')

        self.logger.info(f"Processing Poll Results request for User {user_id}",
                         extra={'RecordId': record_id})

        user_record_db = self.crud_service.get(pk=f'User#{user_id}',
                                               sk=f'Record#{record_id}')
        if not user_record_db:
            self.logger.info("Record does not exists.")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                msg="Invalid Operation or Record does not exists.")
        user_record = RecordOUT(**user_record_db).dict()
        self.logger.info("Returning User record.",
                         extra={'UserRecord': user_record})

        return HTTPResponse(status_code=HTTPStatus.OK,
                            body=user_record)
