from django.core.files.base import ContentFile
from AniQuest.apis.bgm import get_subject
from AniQuest.apis.dandanplay import match
from AniQuest.scrapper.utils import *
from AniQuest.models import Bangumi, Episode
from AniQuest.config import config

import os


class BangumiScrapper:
    def __init__(self):
        self.media_path = config.main["media_path"]

    @logger.catch()
    def scrape(self, bangumi: Bangumi) -> None:
        """
        整理番剧信息，制作nfo文件、下载图片等
        :param bangumi: 该番剧的bangumi实例
        :return: None
        """
        bgm_tv_id = bangumi.bgm_id
        bangumi_name = bangumi.name

        logger.info(f"正在整理番剧： {bgm_tv_id}")
        bangumi_path = os.path.join(self.media_path, bangumi_name)
        if not os.path.exists(bangumi_path):
            os.makedirs(bangumi_path)
        nfo_path = os.path.join(bangumi_path, "tvshow.nfo")
        img_path = os.path.join(bangumi_path, "poster.png")

        bangumi_info: BangumiInfo = get_subject(bgm_tv_id)

        if not bangumi_info["valid"]:
            logger.error(f"爬取失败！")
            return

        xml_tree: ET.ElementTree = make_bangumi_xml(bangumi_info)
        indent(xml_tree.getroot())

        try:
            xml_tree.write(nfo_path, encoding="utf-8")
        except PermissionError as e:
            logger.error(f"权限不足！{e}")
            raise e

        try:
            # 将图片下载至后端数据库，使其能在控制台中显示
            bin_poster = get_image_bin(bangumi_info["image"])
            if bangumi.poster:
                os.remove(bangumi.poster.path)
            bangumi.poster.save(f'{bangumi.id}.jpg', ContentFile(bin_poster), save=True)

            # 将图片下载至视频库，使其能在Jellyfin等媒体库中显示
            download_image(bangumi_info["image"], img_path)
        except Exception as e:
            logger.error(f"无法下载图片至本地！{e}")
            raise e

    def scrape_poster(self, bangumi: Bangumi) -> None:
        """
        挂削海报至前端控制台
        :param bangumi: 该番剧的bangumi实例a
        :return: None
        """
        bangumi_info: BangumiInfo = get_subject(bangumi.bgm_id)

        try:
            # 将图片下载至后端数据库，使其能在控制台中显示
            bin_poster = get_image_bin(bangumi_info["image"])
            if bangumi.poster:
                os.remove(bangumi.poster.path)
            bangumi.poster.save(f'{bangumi.id}.jpg', ContentFile(bin_poster), save=True)

        except Exception as e:
            logger.error(f"无法下载图片至本地！{e}")


class EpisodeScrapper:
    def __init__(self):
        self.file_path = config.main['media_path']
        self.support_types = ["mkv", "mp4"]

    def is_support_type(self, file_name: str) -> bool:
        """
        判断是否是需要挂削的视频类型
        :param file_name: 文件名
        :return: 是否是需要挂削的视频类型
        """
        for t in self.support_types:
            if file_name.endswith(t):
                return True
        return False

    def get_pure_name(self, file_name: str) -> str:
        """
        获取不带扩展名的文件名
        :param file_name: 文件名
        :return: 不带扩展名的文件名
        """
        for t in self.support_types:
            if file_name.endswith(t):
                return file_name.removesuffix(f".{t}")

    @logger.catch()
    def scrape(self, bangumi_id: int, scrape_all: bool = False, no_database: bool = False, bangumi_name: str = None,
               bgm_tv_id: int = 0) -> None:
        logger.info(f"正在为 id: {bangumi_id} 挂削集数信息")

        if no_database:
            bangumi = Bangumi(
                name=bangumi_name,
                rss=None,
                re_rule=None,
                bgm_id=bgm_tv_id,
            )
        else:
            try:
                bangumi = Bangumi.objects.get(id=bangumi_id)
            except Bangumi.DoesNotExist:
                logger.error("不存在该番剧！")
                return

        bangumi_path = os.path.join(self.file_path, bangumi.name)
        if not os.path.exists(bangumi_path):
            os.makedirs(bangumi_path)

        files = os.listdir(bangumi_path)
        for file in files:
            if not self.is_support_type(file):
                continue

            try:
                episode = Episode.objects.get(file_name=file)
            except Episode.DoesNotExist:
                episode = Episode(
                    bangumi=bangumi,
                    file_name=file,
                    scrapped=False
                )

            # 当并非全挂削，且本集已挂削的时候，跳过该集
            if not scrape_all and episode.scrapped:
                continue

            logger.info(f"正在挂削：{file}")

            # 获取匹配dandan api用相关信息
            episode_path = os.path.join(bangumi_path, file)
            hash_data = get_16mb_hash(episode_path)
            file_size = get_file_size(episode_path)

            # 匹配
            episode_info = match(file, hash_data, file_size)
            if not episode_info["valid"]:
                continue

            xml_tree: ET.ElementTree = make_episode_xml(episode_info)
            indent(xml_tree.getroot())

            # 写入nfo文件
            nfo_path = os.path.join(bangumi_path, f"{self.get_pure_name(file)}.nfo")
            try:
                xml_tree.write(nfo_path, encoding="utf-8")
            except PermissionError as e:
                logger.error(f"权限不足！{e}")
            except Exception as e:
                logger.error(f"发生错误！{e}")

            episode.scrapped = True

            if not no_database:
                episode.save()


bangumi_scrapper = BangumiScrapper()

if __name__ == "__main__":
    pass

"""
example:
https://kodi.wiki/view/NFO_files/Templates#tvshow.nfo_Template
https://jellyfin.org/docs/general/server/metadata/nfo/

"""
