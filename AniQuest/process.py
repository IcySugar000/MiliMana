from .models import Bangumi
from AniQuest.scrapper.bangumi import BangumiScrapper


def after_create_bangumi(bangumi: Bangumi):
    """
    在主页面新建任务后进行的处理
    :param bangumi:
    :return:
    """

    # 挂削番剧元数据
    bangumi_scrapper = BangumiScrapper()
    bangumi_scrapper.scrape(bangumi)

    # TODO：将挂削番剧元数据整合入新的API中
