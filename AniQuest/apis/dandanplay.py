import json
import requests
from typing import TypedDict
from AniQuest.config import config


class EpisodeInfo(TypedDict):
    """
    集数信息
    valid: 返回信息是否有效
    episode_id: 集数
    episode_name: 集名
    """
    valid: bool
    id: int
    title: str


def match(file_name: str, file_hash: str, file_size: int) -> EpisodeInfo:
    url = 'https://api.dandanplay.net/api/v2/match'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    post = {
        'fileName': file_name,
        'fileHash': file_hash,
        'fileSize': file_size,
        'videoDuration': 0,
        'matchMode': 'hashAndFileName'
    }
    post_json = json.dumps(post)

    proxies = {'http': config.proxy['http'], 'https': config.proxy['https']}
    if config.proxy['enable']:
        try:
            response = requests.post(url, headers=headers, data=post_json, proxies=proxies)
        except requests.exceptions.ProxyError:
            response = requests.post(url, headers=headers, data=post_json)
    else:
        response = requests.post(url, headers=headers, data=post_json)

    episode_info = EpisodeInfo(
        valid=True,
        id=0,
        title=""
    )

    if response.status_code != 200:
        episode_info["valid"] = False
        return episode_info

    data = response.json()
    if not data['isMatched']:
        episode_info["valid"] = False
        return episode_info
    data = data["matches"][0]  # 取matches列表第一项

    """
    在DandanPlay的数据格式中，episodeId是包含animeId的，如下例：
    episodeId：176170001
    animeId：17617
    因此，通过去除episodeId前面的animeId，再转换成int，我们就能获得集数
    """
    episode_info["id"] = int(str(data["episodeId"]).removeprefix(str(data["animeId"])))
    episode_info["title"] = data["episodeTitle"]

    return episode_info
