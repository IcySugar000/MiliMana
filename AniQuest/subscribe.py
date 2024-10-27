from loguru import logger
from .models import Bangumi
from AniQuest.apis.onebot import send_group_msg
from AniQuest.config import config

ANNOUNCE: list = config.onebot["announce"]


def send_subscribe_msg(bangumi: Bangumi, title: str):
    logger.info("正在发送订阅信息...")

    msg = f"【MiliMana番剧播报】\n" + \
          f"检测到番剧更新！\n" + \
          f"番剧名：{bangumi.name}\n" + \
          f"文件名：{title}"

    for group in ANNOUNCE:
        send_group_msg(group, msg)
