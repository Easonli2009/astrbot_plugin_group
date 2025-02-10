from astrbot.api.provider import ProviderRequest
import astrbot.api.event.filter as filter
from astrbot.api.all import *
from astrbot.core import logger
import random
import time
import json
import asyncio

# json <--> dict 互转辅助类
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding="utf-8")
        if isinstance(obj, int):
            return int(obj)
        if isinstance(obj, float):
            return float(obj)
        if isinstance(obj, chat_history):
             return obj.__dict__
        return super(MyEncoder, self).default(obj)

# 维护历史消息类
class chat_history:
    def __init__(self):
        self.history = list()
        self.history_new = list()
    def new_obj(self, data_dict):
        obj = self
        for attr, val in data_dict.items():
            setattr(obj, attr, val)
        return obj
    def add(self , sth):
        self.history_new.append(sth)
    def get_all(self):
        result1 = ""
        for sth in self.history:
            result1 = result1 + str(sth)
        result2 = ""
        for sth in self.history_new:
            result2 = result2 + str(sth)
        return result1 , result2
    def refresh(self):
        for sth in self.history_new:
            self.history.append(sth)
        self.history_new = []
        while len(self.history) > MAX_HISTORY_COUNT:
            del self.history[0]

INTRODUCTION_OUT = "增强群聊内BOT对话功能，消息平台仅支持aiocqhttp，对于网页及私聊内容无效！\n支持记录群聊内消息记录及新旧消息分离。支持基于消息个数及LLM判断的主动回复，以及被动回复（at）两种发言方式。"
VERSION_SHOW = "1.1.0"
PLUGIN_GROUP_ID = "gourp_increase"
MESSAGE_FILE_PATH = f"data/{PLUGIN_GROUP_ID}_chat_history.json"
MAX_HISTORY_COUNT : int
SYSTEM_PROMPT : str
CHAT_PROMPT : str

dc = dict()
his = dict()
count_recv = 0
count_send = 0
failed_count = 0

# 保存消息
def save_config():
    logger.info("保存消息文件")
    info_json = json.dumps(his, cls = MyEncoder, sort_keys = False, indent = 4)
    file_save = open(MESSAGE_FILE_PATH, "w")
    file_save.write(info_json)

# 读取消息
def read_config():
    logger.info("读取消息文件")
    global readed_config
    readed_config = 1
    if os.path.exists(MESSAGE_FILE_PATH) == True:
        logger.info("已找到消息文件，文件路径为：{MESSAGE_FILE_PATH}")
        file_read = open(MESSAGE_FILE_PATH, "r")
        global his
        his = json.load(file_read)
        tmp_his = dict()
        for key, value in his.items():
            new_value = chat_history()
            new_value = new_value.new_obj(value)
            tmp_his[key] = new_value
        his = tmp_his
    else:
        logger.info("未找到消息文件")

# 获取群员信息
def get_user_in_group_info(obj, group_id, user_id):
    from aiocqhttp import CQHttp
    platforms = obj.context.platform_manager.platform_insts
    aiocqhttp_client: CQHttp = None
    for inst in platforms:
        if inst.meta().name == 'aiocqhttp':
            aiocqhttp_client = inst.bot
            assert isinstance(aiocqhttp_client, CQHttp)
    ret = aiocqhttp_client.api.call_action("get_group_member_info", group_id = group_id, user_id = user_id)
    return ret

# 读取用户面板配置常量
def read_constant(config :dict):
    logger.info("读取用户面板配置")
    logger.debug(f"    all config = {config}")
    global MAX_HISTORY_COUNT, SYSTEM_PROMPT, CHAT_PROMPT
    MAX_HISTORY_COUNT = config["max_history_count"]
    logger.debug(f"    {PLUGIN_GROUP_ID}.MAX_HISTORY_COUNT = {MAX_HISTORY_COUNT}")
    SYSTEM_PROMPT = config["prompt_config"]["system_prompt"]
    logger.debug(f"    {PLUGIN_GROUP_ID}.SYSTEM_PROMPT = {SYSTEM_PROMPT}")
    CHAT_PROMPT = config["prompt_config"]["chat_prompt"]
    logger.debug(f"    {CHAT_PROMPT}.SYSTEM_PROMPT = {CHAT_PROMPT}")

@register(PLUGIN_GROUP_ID, "StrawberryMilk", INTRODUCTION_OUT, VERSION_SHOW)
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        read_constant(config)
        read_config()

    @filter.on_llm_request(priority = -9223372036854775808) # 优先级最低，最后处理消息
    async def process_message(self, event: AstrMessageEvent, llm_request: ProviderRequest): # 处理消息函数
        logger.debug(f"message.platform = {event.get_platform_name()} & type = {event.get_message_type()}")
        if event.get_platform_name() != "aiocqhttp" or event.get_message_type() != MessageType.GROUP_MESSAGE: # 仅 aiocqhttp 消息接收器 & 仅 群聊 消息
            logger.debug("not a valid message!")
            return
        return
    @platform_adapter_type(PlatformAdapterType.AIOCQHTTP) # 仅 aiocqhttp 消息接收器
    @event_message_type(EventMessageType.GROUP_MESSAGE) # 仅 群聊 消息
    async def on_message(self,event : AstrMessageEvent): # 令所有消息均唤醒，方便后续处理
        logger.debug("ok,a valid message!")
        logger.debug(f"收到了：\"{event.get_message_str()}\" 的请求")
        event.stop_event() # 停止传播
        logger.debug("尝试停止事件传播")
        return