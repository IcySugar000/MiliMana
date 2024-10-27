import os
import json
from loguru import logger
from typing import TypedDict, List


class MainConfig(TypedDict):
    media_path: str
    download_interval: int


class ProxyConfig(TypedDict):
    enable: bool
    http: str
    https: str


class BgmConfig(TypedDict):
    user_agent: str
    auth: str


class OnebotConfig(TypedDict):
    enable: bool
    host: str
    announce: List[int]


class QbittorrentConfig(TypedDict):
    save_path: str
    host: str
    port: str
    username: str
    password: str


class Config:
    def __init__(self):
        self.main: MainConfig = None
        self.proxy: ProxyConfig = None
        self.bgm: BgmConfig = None
        self.onebot: OnebotConfig = None
        self.qbittorrent: QbittorrentConfig = None

        self.data = self.load()

        self.mount_data()

    def load(self) -> dict:
        """
        加载Config文件
        :return: Config文件对应字典
        """
        if not os.path.isfile("AniQuest/config.json"):
            logger.info("未检测到config文件，正在创建默认config文件")
            self.create_default_config()

        with open("AniQuest/config.json", "r") as f:
            data = json.load(f)
        return data

    def save(self) -> None:
        """
        保存Config文件
        :return: None
        """
        with open("AniQuest/config.json", "w") as f:
            json.dump(self.data, f)

    def create_default_config(self) -> None:
        """
        创建默认Config文件
        :return: None
        """
        default = {
            "main": {
                "media_path": "/",
                "download_interval": "31112"
            },
            "proxy": {
                "enable": True,
                "http": "http://localhost:7890",
                "https": "http://localhost:7890"
            },
            "bgm": {
                "user_agent": "IcySugar/MiliMana/1.0.0",
                "auth": "HOC9iJtSNRvdz7mpDzw00YIH1l7EauBnw2pdwQEI"
            },
            "onebot": {
                "enable": False,
                "host": "ws://127.0.0.1:8000/api",
                "announce": []
            },
            "qbittorrent": {
                "save_path": "Bangumi",
                "host": "127.0.0.1",
                "port": "8080",
                "username": "admin",
                "password": "adminadmin"
            }
        }

        with open("AniQuest/config.json", "w") as f:
            json.dump(default, f)

    def mount_data(self) -> None:
        """
        将self.data中的信息绑定至各个属性上
        :return: None
        """
        try:
            self.main: MainConfig = self.data["main"]
            self.proxy: ProxyConfig = self.data["proxy"]
            self.bgm: BgmConfig = self.data["bgm"]
            self.onebot: OnebotConfig = self.data["onebot"]
            self.qbittorrent: QbittorrentConfig = self.data["qbittorrent"]
        except KeyError as e:
            logger.error("配置内容错误或缺失！" + e)


config = Config()
