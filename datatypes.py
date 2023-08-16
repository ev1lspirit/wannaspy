from pydantic import BaseModel
from typing import List, Any, TypeVar
from dataclasses import dataclass


@dataclass
class Error:
    error_msg: str
    error_source: Any
    error_type: str


class PhotoURL(BaseModel):
    url: str
    width: int


class Photo(BaseModel):
    id: int
    date: int
    owner_id: int
    sizes: List[PhotoURL]
    has_tags: bool


class Mention(BaseModel):
    date: int
    to_id: int
    from_id: int
    post_type: str
    text: str
    parents_stack: list = None
    id: int = None
    post_id: int = None
    mention_url: str = None


class City(BaseModel):
    id: int
    title: str


class University(BaseModel):
    chair_name: str = None
    city: int = None
    education_form: str = None
    education_status: str = None
    faculty: int = None
    faculty_name: str = None
    graduation: int = None
    name: str = None


class Occupation(BaseModel):
    name: str
    type: str


class Profile(BaseModel):
    id: int
    first_name: str
    last_name: str
    bdate: str = None
    city: City = None
    mobile_phone: str = None
    sex: int = None
    universities: List[University] = None
    occupation: Occupation = None
    platform: str = None
    about: str = None
    deactivated: str = None
    is_closed: bool = False


class Friends(BaseModel):
    items: List[Profile]


class Mentions(BaseModel):
    items: List[Mention]


class APIError(BaseModel):
    error_code: int
    error_msg: str


class Photos(BaseModel):
    items: List[Photo]


class MutualList(BaseModel):
    id: int = None
    common_friends: List[int] = None


ResponseType = TypeVar('ResponseType', Mentions, Friends, Photos, List[MutualList])


class Response(BaseModel):
    response: ResponseType = None
    error: APIError = None


class SingleProfile(BaseModel):
    response: List[Profile] = None
    error: APIError = None
