"""
Common helper/utility functions used to perform arithmetic operations
"""
import math

from shared.models.operation_model import OperationType


def sum_numbers(num1, num2):
    return num1 + num2


def subtract(num1, num2):
    return num1 - num2


def multiply(num1, num2):
    return num1 * num2


def divide(num1, num2):
    return num1 / num2


def square_root(single_number):
    return math.sqrt(single_number)


OPERATION_MAP = {
    OperationType.ADDITION: sum_numbers,
    OperationType.SUBTRACTION: subtract,
    OperationType.MULTIPLICATION: multiply,
    OperationType.DIVISION: divide,
    OperationType.SQUARE_ROOT: square_root
}
