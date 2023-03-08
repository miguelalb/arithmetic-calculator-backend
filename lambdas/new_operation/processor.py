from http import HTTPStatus
from logging import Logger

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService, ConditionType
from shared.json_utils import json_string_to_dict
from shared.models.operation_model import OperationOUT, OperationType
from shared.models.operation_request_msg_model import OperationEventMessage
from shared.models.record_model import RecordOUT
from shared.record_utils import get_user_most_recent_record, is_user_first_operation, check_user_has_sufficient_balance
from shared.sns_service import SnsService
from shared.user_utils import get_user_id_from_cognito_authorizer


class NewOperationEventProcessor:
    def __init__(self,
                 logger: Logger,
                 sns_service: SnsService,
                 crud_service: CrudService,
                 arithmetic_topic_name: str,
                 random_string_topic_name: str
                 ) -> None:
        self.logger = logger
        self.sns_service = sns_service
        self.crud_service = crud_service
        self.arithmetic_topic_name = arithmetic_topic_name
        self.random_string_topic_name = random_string_topic_name

    def process_new_operation_event(self, event: dict) -> HTTPResponse:
        user_id = get_user_id_from_cognito_authorizer(logger=self.logger,
                                                      event=event)
        body = json_string_to_dict(event.get('body', '{}'))
        num1 = body.get('num1')
        num2 = body.get('num2')
        single_number = body.get('single_number')
        operation_type = body.get('operation_type')

        self.logger.info(f"Processing Operation request for User {user_id}",
                         extra={'OperationType': operation_type, 'num1': num1, 'num2': num2})

        topic_name = self._get_topic_name_for_operation_type(operation_type)

        operation_db = self._get_operation_from_db(operation_type)
        operation = OperationOUT(**operation_db)

        operation_event_msg = OperationEventMessage(user_id=user_id,
                                                    num1=num1,
                                                    num2=num2,
                                                    single_number=single_number,
                                                    operation=operation)

        user_records_db = get_user_most_recent_record(crud_service=self.crud_service,
                                                      user_id=user_id)

        if is_user_first_operation(logger=self.logger,
                                   user_records_db=user_records_db):
            message_id = self.sns_service.publish_message(topic_name=topic_name,
                                                          message=operation_event_msg.to_string())
            self.logger.info(f"Sent first operation event for User {user_id}",
                             extra={
                                 'OperationRequest': operation_event_msg.dict(),
                                 'MessageId': message_id
                             })
            return HTTPResponse(status_code=HTTPStatus.OK,
                                body={'RecordId': operation_event_msg.record_id, 'MessageId': message_id})

        user_record = RecordOUT(**user_records_db[0])
        check_user_has_sufficient_balance(logger=self.logger,
                                          operation=operation,
                                          recent_record=user_record)

        message_id = self.sns_service.publish_message(topic_name=topic_name,
                                                      message=operation_event_msg.to_string())
        self.logger.info(f"Sent operation event for User {user_id}",
                         extra={
                             'OperationRequest': operation_event_msg.dict(),
                             'MessageId': message_id
                         })
        return HTTPResponse(status_code=HTTPStatus.OK,
                            body={'RecordId': operation_event_msg.record_id, 'MessageId': message_id})

    def _get_topic_name_for_operation_type(self, operation_type: OperationType) -> str:
        """
        Determines the appropriate SNS topic name to publish a message based on
        the provided OperationType.
        :param operation_type: Operation type to perform
        :return: Topic name to publish a message to
        """
        self.logger.info("Getting correct SNS topic to publish the message to.")
        if operation_type == OperationType.RANDOM_STRING:
            return self.random_string_topic_name
        else:
            return self.arithmetic_topic_name

    def _get_operation_from_db(self, operation_type: OperationType) -> dict:
        """
        Get operation object from DB.
        :param operation_type: The type of operation
        :return: Operation details
        """
        return self.crud_service.list_items(pk='Operation',
                                            gsi1=True,
                                            condition_type=ConditionType.BEGINS_WITH,
                                            condition_value=f'Operation#{operation_type}')[0]
