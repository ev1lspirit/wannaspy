from settings import (
    DefaultAPISettings,
    APIMethods,
    Limits
)
from typing import (
    Union,
    List,
    Optional,
    Dict,
    Callable,
    Generator,
    Set
)
from datatypes import (
    Response,
    Mention,
    Photo,
    SingleProfile,
    Profile,
    MutualList,
    Error
)
from pydantic import ValidationError
from abc import abstractmethod, ABC
from httprequests import Connections
from datetime import datetime
import exceptions
import argparse


def catch_validation_errors(function: Callable) -> Callable:

    def wrapper(response, *args, **kwargs):
        try:
            return function(response, *args, **kwargs)

        except exceptions.RESPONSE_ERRORS as error:
            return Error(
                error_msg=error.message,
                error_source=error.source,
                error_type=error.error_type
            )

        except ValidationError as error:
            error = error.errors()[0]
            return Error(
                error_msg=error.get("msg"),
                error_type=error.get("type"),
                error_source=response
            )
    return wrapper


def validate_response(request: List[Dict]) -> Dict[str, Dict]:
    if not isinstance(request, List):
        raise exceptions.InvalidTypeOfResponseError(
            message=f"Expected type List[dict], got {type(request).__name__} instead.",
            source=f"validate_response, given_data = {request}"
        )

    if not request:
        raise exceptions.EmptyResponseError(
            message=f"Response is empty!",
            source=f"validate_response, given_data = {request}"
        )

    request: dict = request[0]
    if not isinstance(request, dict):
        raise exceptions.InvalidTypeOfResponseError(
            message=f"Expected type List[dict], got List[{type(request).__name__}] instead.",
            source=f"validate_response, given_data = {request}"
        )
    return request


class Parser(ABC):

    @abstractmethod
    def load_data(self) -> Union[Response, Error]:
        pass

    @property
    @abstractmethod
    def response(self):
        pass

    @staticmethod
    def extract_items(response: Response) -> Optional[list]:
        if not isinstance(response, Response):
            return None

        response = response.response
        if not response:
            return None

        items = response.items
        if not items:
            return None

        return items


class ProfileParser(Parser):
    def __init__(self, username: str):
        self.username = self.validate_username(username)
        self.response_from_server = self.load_data()
        self.profile_object = self.get_profile(self.response_from_server)

    @property
    def response(self) -> Union[SingleProfile, Error]:
        return self.response_from_server

    @property
    def profile(self) -> Optional[Profile]:
        return self.profile_object

    @property
    def id(self) -> Optional[int]:
        if self.profile_object:
            return self.profile_object.id
        return None

    @staticmethod
    def validate_username(username: str) -> str:
        if isinstance(username, int):
            username = f"id{username}"

        elif isinstance(username, str):
            if username.isdigit():
                username = f"id{username}"

        else:
            username = str(username)

        return username

    @catch_validation_errors
    def load_data(self) -> Union[SingleProfile, Error]:
        api_link = APIMethods.users_get.format(
            user_id=self.username,
            fields=DefaultAPISettings.request_fields,
            access_token=DefaultAPISettings.access_token,
            version=DefaultAPISettings.api_version
        )
        request = Connections.safe_download(api_link)
        valid_response = validate_response(request)
        return SingleProfile(**valid_response)

    @staticmethod
    def get_profile(profile: Union[SingleProfile, Error]) -> Optional[Profile]:
        if not isinstance(profile, SingleProfile):
            return None

        if profile.error:
            return None

        person = profile.response
        if not person:
            return None

        return person[0]


class MentionsParser(Parser):
    def __init__(self, person_id: int):
        self.person_id = person_id
        self.__mentions_list = self.load_data()
        self.__mentions = self.parse_mentions(self.__mentions_list)

    @property
    def response(self) -> Union[Response, Error]:
        return self.__mentions_list

    @property
    def mentions(self) -> Optional[List[Mention]]:
        return self.__mentions

    @catch_validation_errors
    def load_data(self) -> Union[Response, Error]:
        api_link = APIMethods.newsfeed_getmentions.format(
            owner_id=self.person_id,
            access_token=DefaultAPISettings.user_access_key,
            version=DefaultAPISettings.api_version
        )
        request = Connections.safe_download(api_link)
        valid_request = validate_response(request)
        return Response(**valid_request)

    def create_mention_link(self, mention: Mention) -> Optional[str]:
        reply = "reply"
        post = "post"

        if not all((mention.id, mention.to_id, mention.from_id)):
            return None

        if mention.to_id == self.person_id:
            return None

        if mention.post_type == reply:
            if not mention.post_id:
                return None
            return f"https://vk.com/wall{mention.to_id}_{mention.post_id}?reply={mention.id}"

        elif mention.post_type == post:
            return f"https://vk.com/wall{mention.to_id}_{mention.id}"

        else:
            return None

    def parse_mentions(self, response: Response) -> Optional[List[Mention]]:
        items: List[Mention] = self.extract_items(response)

        if not items:
            return None

        for mention in items:
            mention.mention_url = self.create_mention_link(mention)
            mention.date = self.decode_unix_time(mention.date)

        return items

    @staticmethod
    def decode_unix_time(int_time: int) -> Union[str, int]:
        try:
            return datetime.utcfromtimestamp(int_time).strftime('%Y-%m-%d %H:%M:%S')

        except TypeError:
            return int_time


class PhotoParser(Parser):
    def __init__(self, person_id: int):
        self.person_id = person_id
        self.__response = self.load_data()
        self.__photos = self.parse_photos(self.__response)

    @property
    def response(self) -> Union[Response, Error]:
        return self.__response

    @property
    def photos(self) -> Generator[str, None, None]:
        return self.__photos

    @catch_validation_errors
    def load_data(self) -> Union[Response, Error]:
        api_link = APIMethods.photos_getall.format(
            owner_id=self.person_id,
            access_token=DefaultAPISettings.user_access_key,
            version=DefaultAPISettings.api_version
        )
        request = Connections.safe_download(api_link)
        valid_request = validate_response(request)
        return Response(**valid_request)

    def parse_photos(self, response: Response) -> Generator[str, None, None]:
        items: List[Photo] = self.extract_items(response)
        if not items:
            return None

        for photo in items:
            sizes = photo.sizes
            if sizes:
                yield sizes[-1]


class FriendsParser(Parser):

    def __init__(self, person_id: int):
        self.person_id = person_id
        self.friends_response = self.load_data()
        self.friends_ = self.parse_friends(self.friends_response)
        self.__most_common_city = None
        self.__average_age = None
        self.__most_common_university = None

    @property
    def response(self) -> Union[Response, Error]:
        return self.friends_response

    def __repr__(self):
        return str(self.friends_)

    @property
    def friends(self) -> Optional[List[Profile]]:
        if self.friends_:
            return self.friends_
        return None

    @property
    def possible_city(self) -> tuple:
        if not self.__most_common_city:
            self.__most_common_city = self.count_friends_cities(self.friends_)

        return self.__most_common_city

    @property
    def friends_average_age(self) -> float:
        if self.__average_age is None:
            self.__average_age = self.calculate_average_age(self.friends_)

        return self.__average_age

    @property
    def most_frequent_university(self):
        if self.__most_common_university is None:
            self.__most_common_university = self.count_universities(self.friends_)

        return self.__most_common_university

    @catch_validation_errors
    def load_data(self) -> Union[Response, Error]:
        api_link = APIMethods.friends_get.format(
            user_id=self.person_id,
            fields=DefaultAPISettings.request_fields,
            access_token=DefaultAPISettings.access_token,
            version=DefaultAPISettings.api_version
        )
        request = Connections.safe_download(api_link)
        valid_request = validate_response(request)
        return Response(**valid_request)

    def parse_friends(self, response: Response) -> Optional[List[Profile]]:
        items: List[Profile] = self.extract_items(response)
        return items

    @staticmethod
    def __get_university(profile: Profile) -> Optional[str]:
        universities_ = profile.universities
        if not universities_:
            return None

        university_name = universities_[0].name

        if university_name:
            return university_name
        return None

    @staticmethod
    def __get_occupation(profile: Profile) -> Optional[str]:
        university_type = "university"
        occupation = profile.occupation
        if not occupation:
            return None

        occupation_type = occupation.type
        if occupation_type != university_type:
            return None

        occupation_name = occupation.name
        if occupation_name:
            return occupation_name
        return None

    def count_universities(self, items: List[Profile]) -> Optional[tuple]:
        if not items:
            return ()

        friends_universities = {}
        for friend in items:
            occupation = self.__get_occupation(friend)
            university_name = self.__get_university(friend)

            if occupation:
                university = occupation

            elif university_name:
                university = university_name

            else:
                continue

            if university in friends_universities:
                friends_universities[university] += 1

            else:
                friends_universities[university] = 1

        if friends_universities:
            most_common: tuple = max(zip(friends_universities.values(), friends_universities.keys()))
            return most_common

        return None

    @staticmethod
    def count_friends_cities(items: List[Profile]) -> tuple:
        if not items:
            return ()

        friends_cities = {}
        for friend in items:
            if not friend.city:
                continue

            title = friend.city.title
            if not title:
                continue

            if title in friends_cities:
                friends_cities[title] += 1
            else:
                friends_cities[title] = 1

        if friends_cities:
            most_frequent: tuple = max(zip(friends_cities.values(), friends_cities.keys()))
            return most_frequent

        return ()

    @staticmethod
    def __convert_birth_date_to_age(birth_date: str) -> Optional[int]:
        birth_date = birth_date.split(".")
        if len(birth_date) != 3:
            return None

        birth_year = birth_date[2]
        if len(birth_year) != 4:
            return None

        if not birth_year.isdigit():
            return None

        return datetime.now().year - int(birth_year)

    def calculate_average_age(self, friends: List[Profile]) -> float:
        if not friends:
            return 0.0

        total = 0
        count = 0

        for friend in friends:
            if not friend.bdate:
                continue

            age = self.__convert_birth_date_to_age(friend.bdate)
            if not age:
                continue

            total += age
            count += 1

        return round(total / count, 1)


class MutualParser(Parser):
    def __init__(self, user_id: int, friends_list: List[Profile]):
        self.user_id = user_id
        self.friends_list = friends_list
        self.__response = self.load_data()

    def __get_only_available_profiles(self):
        if not self.friends_list:
            return None

        for friend in self.friends_list:
            filters = (friend.deactivated, friend.is_closed)
            if any(filters):
                continue

            yield friend

    def __convert_friend_list_into_sublist(self) -> List[Set[str]]:
        limit = Limits.getmutual_limit
        list_of_sublists = []
        list_of_elements = set()

        for counter, friend in enumerate(self.__get_only_available_profiles()):
            if counter % limit == 0 and counter:
                list_of_sublists.append(list_of_elements)
                list_of_elements = set()
                continue

            list_of_elements.add(str(friend.id))

        if list_of_elements:
            list_of_sublists.append(list_of_elements)

        return list_of_sublists

    @catch_validation_errors
    def load_data(self) -> Generator[Response, None, Optional[Error]]:
        available_uids = self.__convert_friend_list_into_sublist()

        if not available_uids:
            return

        for uids in available_uids:
            api_link = APIMethods.get_mutual.format(
                source_uid=self.user_id,
                target_uids=",".join(uids),
                access_token=DefaultAPISettings.user_access_key,
                version=DefaultAPISettings.api_version
            )
            request = Connections.safe_download(api_link)
            valid_request = validate_response(request)
            yield Response(**valid_request)

    @property
    def response(self) -> Generator[Response, None, Optional[Error]]:
        return self.__response

    def get_mutual_friends(self) -> Generator[MutualList, None, None]:
        response_objects = (object_.response for object_ in self.response if not object_.error)
        for mutual_object in response_objects:
            yield from mutual_object

    def count_mutual_friends(self):
        for mutual in self.get_mutual_friends():
            yield mutual.id, len(mutual.common_friends)


def main():
    obj = ProfileParser("") #loganovas
    if isinstance(obj, Error):
        print(obj)
        return

    if obj.profile.is_closed or obj.profile.deactivated:
        print(obj.profile)
        print("Unavailable")
        return

    frnds = FriendsParser(obj.id)
    print(frnds)
    mutual = MutualParser(obj.id, frnds.friends)
    for idx, i in enumerate(mutual.count_mutual_friends()):
        print(i)


if __name__ == "__main__":
    main()
