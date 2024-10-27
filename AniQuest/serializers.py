from rest_framework import serializers
from AniQuest.models import *


class BangumiSerializer(serializers.ModelSerializer):
    poster = serializers.CharField(read_only=True)

    class Meta:
        model = Bangumi
        fields = '__all__'


"""
--------------------------
↓ 配置项相关的Serializer ↓
--------------------------
"""


class MainConfigSerializer(serializers.Serializer):
    media_path = serializers.CharField()
    download_interval = serializers.IntegerField()


class ProxyConfigSerializer(serializers.Serializer):
    enable = serializers.BooleanField()
    http = serializers.CharField()
    https = serializers.CharField()


class BgmConfigSerializer(serializers.Serializer):
    user_agent = serializers.CharField()
    auth = serializers.CharField()


class OnebotConfigSerializer(serializers.Serializer):
    enable = serializers.BooleanField()
    host = serializers.CharField()
    announce = serializers.ListField(
        child=serializers.IntegerField()
    )


class QbittorrentConfigSerializer(serializers.Serializer):
    save_path = serializers.CharField()
    host = serializers.CharField()
    port = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()


class ConfigSerializer(serializers.Serializer):
    main = MainConfigSerializer()
    proxy = ProxyConfigSerializer()
    bgm = BgmConfigSerializer()
    onebot = OnebotConfigSerializer()
    qbittorrent = QbittorrentConfigSerializer()
