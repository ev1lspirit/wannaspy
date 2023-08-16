from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class DefaultAPISettings:
    access_token: str = getenv("ACCESS_TOKEN")
    user_access_key: str = getenv("USER_ACCESS_TOKEN")
    request_fields = "about,activities,occupation,bdate,city,connections,contacts,counters," \
                     "relatives,sex,universities,last_seen"
    api_version = "5.131"


@dataclass(frozen=True)
class APIMethods:
    users_get = r"https://api.vk.com/method/users.get?user_ids={user_id}&fields={fields}&" \
                r"access_token={access_token}&v={version}"
    friends_get = r"https://api.vk.com/method/friends.get?user_id={user_id}&count=500&fields={fields}" \
                  r"&access_token={access_token}&v={version}"
    likes_getlist = r"https://api.vk.com/method/likes.getList?type=post&owner_id={owner_id}&item_id={item_id}" \
                    r"&filter=likes&count={count}&skip_own=1&access_token={access_token}&v={version}"
    get_mutual = r"https://api.vk.com/method/friends.getMutual?source_uid={source_uid}&target_uids={target_uids}" \
                 r"&count=500&access_token={access_token}&v={version}"
    wall_get = r"https://api.vk.com/method/wall.get?owner_id={owner_id}&count=100" \
               r"&extended=1&access_token={access_token}&v={version}"
    photos_get = r"https://api.vk.com/method/photos.get?owner_id={owner_id}&" \
                 r"album_id={album_id}&photo_sizes=1&extended=0&count=100" \
                 r"&access_token={access_token}&v={version}"
    photos_getall = r"https://api.vk.com/method/photos.getAll?owner_id={owner_id}&need_hidden=1&extended=1" \
                    r"&access_token={access_token}&v={version}"
    photos_gettags = r"https://api.vk.com/method/photos.getTags?owner_id={owner_id}&photo_id={photo_id}" \
                     r"&access_token={access_token}&v={version}"
    newsfeed_getmentions = r"https://api.vk.com/method/newsfeed.getMentions?owner_id={owner_id}" \
                           r"&count=50&access_token={access_token}&v={version}"


@dataclass(frozen=True)
class Limits:
    getmutual_limit = 190