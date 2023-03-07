"""
Common helper/utility functions used for User entity
"""
from logging import Logger


def get_user_id_from_cognito_authorizer(logger: Logger, event: dict) -> str:
    """
    Extracts the user_id provided by the Amazon Cognito authorizer.
    :param logger: logger
    :param event: Lambda event
    :return: User_id
    """
    logger.info("Extracting the user id from the request.")
    return event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub', '')
