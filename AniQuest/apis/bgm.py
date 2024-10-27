import json
import requests
from loguru import logger
from typing import TypedDict
from pathlib import Path
from AniQuest.config import config

PROXIES = {'http': config.proxy['http'], 'https': config.proxy['https']}
USER_AGENT = config.bgm["user_agent"]
AUTH = config.bgm["auth"]
POSTER_PATH = "AniQuest/static/AniQuest/posters"


class BangumiInfo(TypedDict):
    """
    返回信息类
    valid: 访问是否成功
    name_cn: 中文名
    image: 海报图片url
    summary: 简介
    date: 上映日期
    """
    valid: bool
    name_cn: str
    image: str
    summary: str
    date: str


def get_subject(subject_id: int) -> BangumiInfo:
    logger.info(f"正在爬取番剧数据: {subject_id}")

    bangumi_info = BangumiInfo(
        valid=True,
        name_cn="",
        image="",
        summary="",
        date="",
    )

    # 抓取番剧信息
    url = f"https://api.bgm.tv/v0/subjects/{subject_id}"
    headers = {"User-Agent": USER_AGENT,
               "Authorization": f"Bearer {AUTH}"}
    if config.proxy['enable']:
        try:
            response = requests.get(url,
                                    proxies=PROXIES,
                                    headers=headers)
        except requests.exceptions.ProxyError:
            response = requests.get(url,
                                    headers=headers)
    else:
        response = requests.get(url,
                                headers=headers)
    # 访问不成功
    if response.status_code != 200:
        bangumi_info["valid"] = False
        logger.error(f"未找到该番剧!")
        return bangumi_info

    response_json = json.loads(response.text)
    bangumi_info["name_cn"] = response_json["name_cn"]
    bangumi_info["image"] = response_json["images"]["large"]
    bangumi_info["summary"] = response_json["summary"]
    bangumi_info["date"] = response_json["date"]
    return bangumi_info


def get_poster(bgm_id: int, self_id: int):
    try:
        url = f"https://api.bgm.tv/v0/subjects/{bgm_id}"
        headers = {"User-Agent": USER_AGENT,
                   "Authorization": f"Bearer {AUTH}"}
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if 'title' in result:
            if result['title'] == "Not Found":
                return None
        img_url = result['images']['large']
        r = requests.get(img_url)

        poster = Path(f"{POSTER_PATH}/{self_id}.jpg")
        poster.touch(exist_ok=True)
        with open(poster, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        logger.error(f"获取海报失败：{e}")


if __name__ == "__main__":
    ...
