import os
import re
import requests
import xmltodict
from loguru import logger
from random import randint
from qbittorrentapi import Client
from django.utils import timezone
from .models import Bangumi, Record
from .subscribe import send_subscribe_msg
from .scrapper.bangumi import EpisodeScrapper
from .config import config


@logger.catch()
def download_bangumi():
    logger.info("开始检查下载任务...")

    SAVE_PATH = config.qbittorrent["save_path"]
    PROXIES = {'http': config.proxy['http'], 'https': config.proxy['https']}
    QB_HOST = config.qbittorrent["host"]
    QB_PORT = config.qbittorrent["port"]
    QB_USERNAME = config.qbittorrent["username"]
    QB_PASSWORD = config.qbittorrent["password"]

    qb = Client(
        host=QB_HOST,
        port=QB_PORT,
        username=QB_USERNAME,
        password=QB_PASSWORD
    )

    def get_xml(url):  # 获取rss链接内容的xml
        # 有代理时优先使用代理，不然使用直连
        if config.proxy['enable']:
            try:
                response = requests.get(url, proxies=PROXIES)
                return response.text
            except requests.exceptions.ProxyError as proxy_err:
                logger.error(f"代理连接失败！{proxy_err}")
                logger.info("尝试直接连接")
                response = requests.get(url)
                return response.text
        else:
            response = requests.get(url)
            return response.text

    def get_items(xml_txt):  # 获取xml内的每一个项目
        # print(xml_txt)
        dic = xmltodict.parse(xml_txt)
        return dic["rss"]["channel"]["item"]

    def download(name, link):  # 下载种子并上传
        logger.info(f"正在下载种子: {link}")
        save_path = SAVE_PATH + "/" + name
        torrent_path = f"AniQuest/data/torrents/{randint(1, 100)}.torrent"

        # 如果torrent文件夹不存在，则创建
        if not os.path.exists(torrent_path):
            os.makedirs(torrent_path)

        # 下载临时种子文件，有代理时优先使用代理，不然使用直连
        if config.proxy['enable']:
            try:
                response = requests.get(link, proxies=PROXIES, stream=True)
            except requests.exceptions.ProxyError as proxy_err:
                logger.error(f"代理连接失败！{proxy_err}")
                logger.info("尝试直接连接")
                response = requests.get(link, stream=True)
        else:
            response = requests.get(link, stream=True)
        with open(torrent_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=512):
                f.write(chunk)

        qb.torrents_add(torrent_files=torrent_path, save_path=save_path)
        # qb.torrents_add(urls=link, save_path=save_path)

    active_tasks = Bangumi.objects.filter(archived=False)
    for task in active_tasks:
        xml = get_xml(task.rss)
        items = get_items(xml)
        if type(items) is not list:  # 防止items在仅有一个项目的时候不为列表
            items = [items]
        for item in items:
            # 排除所有不符合规则的项目
            if task.re_rule:
                # logger.debug(f"{task.re_rule}, {item['title']}, {re.search(task.re_rule, item['title'])}")
                if not re.search(task.re_rule, item["title"]):
                    if not Record.objects.filter(file_name=item["title"]):
                        # 记录未下载信息
                        new_record = Record(
                            bangumi=task,
                            file_name=item["title"],
                            have_downloaded=False,
                            download_time=timezone.now()
                        )
                        new_record.save()
                    continue
            exist = Record.objects.filter(file_name=item["title"], have_downloaded=True).exists()  # 是否已经存在该记录
            # 排除数据库内存在且已下载的项目
            if exist:
                continue

            # 下载种子
            logger.info(f"正在下载： {task.name} - {item['title']}")
            try:
                download(task.name, item["enclosure"]["@url"])
                if not exist:
                    new_record = Record(
                        bangumi=task,
                        file_name=item["title"],
                        have_downloaded=True,
                        download_time=timezone.now()
                    )
                    new_record.save()
                else:
                    exist_record = Record.objects.get(file_name=item["title"])
                    exist_record.have_downloaded = True
                    exist_record.save()

                # 通报下载信息
                if config.onebot['enable']:
                    send_subscribe_msg(task, item["title"])
            except Exception as e:
                logger.error(f"下载失败！{e}")

        scrapper = EpisodeScrapper()
        scrapper.scrape(task.id)


# TODO: 新增一个每小时循环一次的全挂削任务，防止挂削有误
