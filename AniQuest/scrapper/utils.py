import os
import hashlib
import requests
import xml.etree.cElementTree as ET
from loguru import logger
from AniQuest.apis.bgm import BangumiInfo
from AniQuest.apis.dandanplay import EpisodeInfo


def download_image(url: str, path: str) -> None:
    """
    下载图片
    :param url: 图片url
    :param path: 图片保存地址
    :return: None
    """
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        logger.error(f"下载图片时发生错误！{e}")


def get_image_bin(url: str) -> bytes:
    """
    返回图片的二进制形式
    :param url: 图片url
    :return: 图片的二进制形式数据
    """
    r = requests.get(url, stream=True)
    return r.content


def indent(elem: ET.Element, level: int = 0) -> None:
    """
    为xml文本提供缩进，美化格式
    :param elem: ElementTree的根节点
    :param level: 缩进量
    :return: None
    """
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def make_bangumi_xml(bangumi_info: BangumiInfo) -> ET.ElementTree:
    """
    制作tvshows.nfo文件中的xml格式信息
    :param bangumi_info: 搜刮到的BangumiInfo信息
    :return: xml信息的ElementTree实例
    """
    root = ET.Element("tvshow")

    # 标题
    title = ET.SubElement(root, "title")
    title.text = bangumi_info["name_cn"]
    # 简介
    plot = ET.SubElement(root, "plot")
    plot.text = bangumi_info["summary"]
    # 海报
    poster = ET.SubElement(root, "thumb", aspect="poster", preview="poster.png")
    poster.text = "poster.png"
    # 年份
    year = ET.SubElement(root, "year")
    year.text = bangumi_info["date"].split('-')[0]

    tree = ET.ElementTree(root)
    return tree


def make_episode_xml(episode_info: EpisodeInfo) -> ET.ElementTree:
    """
    制作集数nfo文件中的xml格式信息
    :param episode_info: 搜刮到的EpisodeInfo信息
    :return: xml信息的ElementTree实例
    """
    root = ET.Element("episodedetails")

    # 标题
    title = ET.SubElement(root, "title")
    title.text = episode_info["title"]
    # 集数
    episode = ET.SubElement(root, "episode")
    episode.text = str(episode_info["id"])

    tree = ET.ElementTree(root)
    return tree


def get_file_size(episode_path: str) -> int:
    """
    获取文件大小
    :param episode_path: 文件路径
    :return: 文件大小
    """
    file_size = os.stat(episode_path).st_size
    return file_size


def get_16mb_hash(episode_path: str) -> str:
    """
    获取文件前16mb哈希值
    :param episode_path: 文件路径
    :return: 哈希值
    """
    with open(episode_path, "rb") as f:
        hash_data = f.read(16 * 1024 * 1024)
        hash_info = hashlib.md5(hash_data).hexdigest()
        return hash_info
