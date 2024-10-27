import json
import asyncio
import websockets
from loguru import logger
from AniQuest.config import config

HOST = config.onebot["host"]


def send_private_msg(user_id: int, message: str):
    async def send_private():
        async with websockets.connect(HOST) as socket:
            msg = {
                "action": "send_private_msg",
                "params": {
                    "user_id": user_id,
                    "message": message
                },
            }
            json_message = json.dumps(msg)
            await socket.send(json_message)

            response = await socket.recv()
            json_response: dict = json.loads(response)
            if "status" in json_response.keys():
                if json_response["status"] == "ok":
                    logger.info("私人消息发送成功")
    asyncio.run(send_private())


def send_group_msg(group_id: int, message: str):
    async def send_group():
        async with websockets.connect(HOST) as socket:
            msg = {
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": message
                },
            }
            json_message = json.dumps(msg)
            await socket.send(json_message)

            response = await socket.recv()
            json_response: dict = json.loads(response)
            if "status" in json_response.keys():
                if json_response["status"] == "ok":
                    logger.info("群聊消息发送成功")

    asyncio.run(send_group())
