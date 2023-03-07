from http import HTTPStatus
from logging import Logger

from shared.api_utils import HTTPResponse
from shared.crud_service import CrudService, ConditionType
from shared.date_utils import get_js_utc_now
from shared.error_handling import HTTPException
from shared.json_utils import json_str_to_dict
from shared.models.operation_model import OperationOUT, OperationType
from shared.models.operation_request_msg_model import OperationEventMessage
from shared.models.record_model import RecordOUT
from shared.sns_service import SnsService


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
        user_id = self._get_user_id(event)
        body = json_str_to_dict(event.get('body', '{}'))
        num1 = body.get('num1')
        num2 = body.get('num2')
        operation_type = body.get('operation_type')

        self.logger.info(f"Processing Operation request for User {user_id}",
                         extra={'OperationType': operation_type, 'num1': num1, 'num2': num2})

        topic_name = self._get_topic_name_for_operation_type(operation_type)

        operation_db = self._get_operation_from_db(operation_type)
        operation = OperationOUT(**operation_db)

        operation_event_msg = OperationEventMessage(user_id=user_id,
                                                    num1=num1,
                                                    num2=num2,
                                                    operation=operation)

        user_records_db = self._get_user_most_recent_record(user_id)

        if self._is_user_first_operation(user_records_db):
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
        self._check_user_has_sufficient_balance(operation, user_record)

        message_id = self.sns_service.publish_message(topic_name=topic_name,
                                                      message=operation_event_msg.to_string())
        self.logger.info(f"Sent operation event for User {user_id}",
                         extra={
                             'OperationRequest': operation_event_msg.dict(),
                             'MessageId': message_id
                         })
        return HTTPResponse(status_code=HTTPStatus.OK,
                            body={'RecordId': operation_event_msg.record_id, 'MessageId': message_id})

    def _check_user_has_sufficient_balance(self, operation: OperationOUT, recent_record: RecordOUT) -> None:
        """
        Checks if the user has sufficient balance to cover for the operation cost
        :param operation: The operation the user wants to perform
        :param recent_record: The most recent user Record.
        :return: None
        """
        self.logger.info("Checking that the user has sufficient balance.")
        if recent_record.user_balance < operation.cost:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg='Insufficient Funds to perform this operation')

    def _get_user_id(self, event: dict) -> str:
        """
        Extracts the user_id provided by the Amazon Cognito authorizer.
        :param event: Lambda event
        :return: User_id
        """
        self.logger.info("Extracting the user id from the request.")
        return event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', '')

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

    def _get_user_most_recent_record(self, user_id: str) -> list:
        """
        Gets the user's most recent Record.
        :param user_id: ID of the user
        :return: Record DB object
        """
        return self.crud_service.list_items(pk=f'User#{user_id}',
                                            gsi1=True,
                                            ascending=False,
                                            limit=1,
                                            condition_type=ConditionType.LESS_THAN_OR_EQUAL,
                                            condition_value=f'Record#{get_js_utc_now()}')

    def _is_user_first_operation(self, user_records_db: list) -> bool:
        """
        Each user has an initial credit/balance. If this user doesn't have an operation
        history it means this is their first time they're doing an operation.

        The initial balance will be granted (and operation costs deducted from it) in
        the downstream worker lambda that processes the operation event message.
        :param user_records_db: User Recent Records
        :return: True if this is the first user operation, otherwise False
        """
        self.logger.info("Checking if this is the user's first operation.")
        return not user_records_db
