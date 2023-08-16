from dataclasses import dataclass
from typing import Any
from pydantic import ValidationError


@dataclass
class APIError:
    error_code: int
    error_msg: str
    error_source: Any


@dataclass
class ConnectionError(Exception):
    message: str
    source: Any
    error_type = "exceptions.ConnectionError"
    description = "[Error] Connection error! Please, check if you're connected to the internet."


@dataclass
class EmptyResponseError(KeyError):
    message: str
    source: Any
    error_type = "exceptions.EmptyResponseError(KeyError)"
    description = "[Error] Server response is empty! Please, check if request parameters is correct."


@dataclass
class InvalidResponseError(KeyError):
    error_type = "exceptions.InvalidResponseError(KeyError)"
    description = "[Error] Invalid response!"


@dataclass
class InvalidTypeOfResponseError(TypeError):
    message: str
    source: Any
    error_type = "exceptions.InvalidTypeOfResponseError(TypeError)"
    description = "[Error] Type of response is not valid!"


@dataclass
class BadValidationError(ValidationError):
    message: str
    source: Any
    error_type = "exceptions.BadValidationError(ValidationError)"
    description = ""


@dataclass
class RequestError(Exception):
    message: str
    source: Any
    error_type = "exceptions.RequestError"
    description = "[Error] Request Error! Status code is not [200] OK."


RESPONSE_ERRORS = (EmptyResponseError, InvalidTypeOfResponseError)
