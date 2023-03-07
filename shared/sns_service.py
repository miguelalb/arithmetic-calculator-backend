from http import HTTPStatus

from botocore.exceptions import ClientError
from logging import Logger

from shared.error_handling import HTTPException


class SnsService:
    """
    Encapsulates Amazon SNS topic and subscription functions
    """
    def __init__(self,
                 logger: Logger,
                 sns_client
                 ) -> None:
        self.logger = logger
        self.sns_client = sns_client

    def _get_topic_arn(self, topic_name: str) -> str:
        """
        Gets the ARN from the topic name
        :param topic_name: name of the topic
        :return: ARN
        """
        try:
            return self.sns_client.create_topic(Name=topic_name)['TopicArn']

        except ClientError as err:
            self.logger.exception("There was an error trying to get the topic name.",
                                  extra={'Exception': err})
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                msg="Oops something went wrong.")

    def publish_message(self, topic_name: str, message: str, attributes: dict = None) -> str:
        """
        Publishes a message, with attributes, to a topic. Subscriptions can be filtered
        based on message attributes so that a subscription receives messages only
        when specified attributes are present.
        :param topic_name: The topic to publish to.
        :param message: The message to publish.
        :param attributes: The key-value attributes to attach to the message. Values
                           must be either `str` or `bytes`.
        :return str: The ID of the message.
        """
        try:
            payload = {}
            if attributes:
                att_dict = {}
                for key, value in attributes.items():
                    if isinstance(value, str):
                        att_dict[key] = {'DataType': 'String', 'StringValue': value}
                    elif isinstance(value, bytes):
                        att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
                payload['MessageAttributes'] = att_dict

            topic_arn = self._get_topic_arn(topic_name=topic_name)
            payload['TopicArn'] = topic_arn
            payload['Message'] = message

            response = self.sns_client.publish(**payload)
            self.logger.info(f"Published message to topic: {topic_arn} attributes: {attributes} ")

            return response['MessageId']

        except ClientError as err:
            self.logger.exception("There was an error trying to publish a message to the topic",
                                  extra={'Exception': err, 'topic_name': topic_name})
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                msg="Oops something went wrong.")

