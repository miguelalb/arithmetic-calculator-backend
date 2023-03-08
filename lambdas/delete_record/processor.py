from http import HTTPStatus
from logging import Logger

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService
from shared.error_handling import HTTPException
from shared.models.record_model import RecordOUT
from shared.user_utils import get_user_id_from_cognito_authorizer


class DeleteRecordProcessor:
    def __init__(self,
                 logger: Logger,
                 crud_service: CrudService
                 ) -> None:
        self.logger = logger
        self.crud_service = crud_service

    def process_delete_record_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)
        record_id = event.get('pathParameters', {}).get('record_id', '')

        self.logger.info(f"Processing Delete Record request for User {user_id}",
                         extra={'RecordId': record_id})

        delete_record_payload = {
            'pk': f'User#{user_id}',
            'sk': f'Record#{record_id}',
            'update_expression': 'SET #deleted = :deleted',
            'expression_attribute_names': {
                '#deleted': 'deleted'
            },
            'expression_attribute_values': {
                ':deleted': True
            }
        }

        self.logger.info(f"Sending update request to Record {record_id}",
                         extra={'DeleteRecordPayload': delete_record_payload})
        user_record_db = self.crud_service.update_item_attributes(**delete_record_payload)
        if not user_record_db:
            self.logger.info("Record does not exists.")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                                msg="Record does not exists.")
        user_record = RecordOUT(**user_record_db).dict()
        self.logger.info("Returning user record marked as 'deleted'.",
                         extra={'UserRecord': user_record})

        return HTTPResponse(status_code=HTTPStatus.OK,
                            body=user_record)
