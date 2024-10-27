from loguru import logger

from django.conf import settings
from django.shortcuts import render

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status

from AniQuest.models import Bangumi
from AniQuest.task import download_bangumi
from AniQuest.serializers import BangumiSerializer, ConfigSerializer
from AniQuest.scrapper.bangumi import bangumi_scrapper
from AniQuest.config import config
from AniQuest.process import after_create_bangumi

# 任务调度器作为全局变量
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), "default")


def index(request):
    return render(request, "index.html")


class BangumiViewSet(viewsets.ModelViewSet):
    """
    和Bangumi相关的增删改查API

    注意：poster字段是只读的
    """
    queryset = Bangumi.objects.all()
    serializer_class = BangumiSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bangumi = serializer.save()
        after_create_bangumi(bangumi)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ScrapeBangumiView(APIView):
    """
    挂削某番剧的全部信息
    """

    serializer_class = None

    def get(self, request, pk):
        try:
            bangumi = Bangumi.objects.get(pk=pk)
        except Bangumi.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            bangumi_scrapper.scrape(bangumi)
        except Exception as e:
            logger.error(f"挂削番剧时出现错误！{e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class ScrapeBangumiPosterView(APIView):
    """
    挂削某番剧的控制台海报
    """

    serializer_class = None

    def get(self, request, pk):
        try:
            bangumi = Bangumi.objects.get(pk=pk)
        except Bangumi.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            bangumi_scrapper.scrape_poster(bangumi)
        except Exception as e:
            logger.error(f"挂削海报时出现错误！{e}")
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class ConfigViewSet(APIView):
    serializer_class = ConfigSerializer

    def get(self, request):
        serializer = ConfigSerializer(config)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConfigSerializer(data=request.data)
        if serializer.is_valid():
            new_config = serializer.validated_data
            config.data = new_config
            config.mount_data()
            config.save()

            # 更改定时任务时间
            scheduler.reschedule_job('download_bangumi',
                                     trigger=IntervalTrigger(minutes=config.main['download_interval'])
                                     )

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


def main() -> None:
    """
    主函数
    用于执行开启django时的一些行为
    :return:
    """

    # 定时任务部分
    try:
        logger.info("正在启动定时任务...")

        scheduler.add_job(
            download_bangumi,
            'interval',
            minutes=10000,
            id="download_bangumi",
            max_instances=1,
            replace_existing=True,
        )

        scheduler.start()
        logger.info("定时任务启动完毕")
    except Exception as e:
        logger.error(f"定时任务启动失败！{e}")


main()
