from astrbot.api.all import *
import random
import time
import json
import asyncio

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

MAX_HISTORY_COUNT : int
SYSTEM_PROMPT : str
CHAT_PROMPT : str

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


dc = dict()
his = dict()
count_recv = 0
count_send = 0
failed_count = 0

def save_config():
    info_json = json.dumps(his, cls = MyEncoder, sort_keys = False, indent = 4)
    file_save = open("group_config.json", "w")
    file_save.write(info_json)

def read_config():
    print("Function: read_config")
    global readed_config
    readed_config = 1
    if os.path.exists("group_config.json") == True:
        file_read = open("group_config.json", "r")
        global his
        his = json.load(file_read)
        tmp_his = dict()
        for key, value in his.items():
            print("pair of key & value:")
            print("#key = ", key)
            print("#value = ",value)
            new_value = chat_history()
            new_value = new_value.new_obj(value)
            tmp_his[key] = new_value
        his = tmp_his

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

func_call_inst = None

def init_func_call(obj):
    from astrbot.core.provider.func_tool_manager import FuncCall
    global func_call_inst
    func_call_inst = obj.context.get_llm_tool_manager()
    print("func_call_inst", func_call_inst.__dict__)

is_inited = False

def init_group_plugin(obj):
    read_config()
    print("--------------")
    init_func_call(obj)
    global is_inited
    is_inited = True

@register("group", "Lyz09", "我的插件", "1.0.5")
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        print("group_config: ", self.config)
        global MAX_HISTORY_COUNT
        MAX_HISTORY_COUNT = self.config["max_history_count"]
        print("#MAX_HISTORY_COUNT = ", MAX_HISTORY_COUNT)
        global SYSTEM_PROMPT
        SYSTEM_PROMPT = self.config["prompt_config"]["system_prompt"]
        print("#SYSTEM_PROMPT = ", SYSTEM_PROMPT)
        global CHAT_PROMPT
        CHAT_PROMPT = self.config["prompt_config"]["chat_prompt"]
        print("#CHAT_PROMPT = ", CHAT_PROMPT)
    
    @command("test")
    async def test(self, event: AstrMessageEvent):
        if False or True:
                from astrbot.core.provider.func_tool_manager import FuncCall
                func_call_inst = FuncCall()
                event.stop_event() # 停止事件传播
                yield 0

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器
    async def on_message(self,event : AstrMessageEvent):
        event.stop_event() # 停止事件传播
        if is_inited == False:
            init_group_plugin(self)
        # print("#Debug Message: ")
        # print(event.message_obj.raw_message) # 打印消息内容
        group_id=event.get_group_id()
        print("#group id=" + group_id)
        print("#sender.id=" + str(event.message_obj.sender.user_id))
        print("#sender.nickname=" + str(event.message_obj.sender.nickname))
        print("#time=" + str(event.message_obj.timestamp))
        real_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.message_obj.timestamp))
        print("#real_time=" + real_time)
        print("#message=" + str(event.message_obj.message))
        print("#message_real=" + str(event.get_message_outline()))
        global dc
        if group_id not in dc:
            dc[group_id] = random.randint(3,8)
        if group_id not in his or not isinstance(his[group_id], chat_history):
            his[group_id] = chat_history()
        dc[group_id] = int(dc.get(group_id)) - 1
        this_msg = dict()
        this_msg["Time"] = real_time
        this_msg["User_ID"] = str(event.message_obj.sender.user_id)
        this_msg["Name"] = str(event.message_obj.sender.nickname)
        tmp_user_info = await get_user_in_group_info(obj = self, group_id = event.message_obj.group_id, user_id = event.get_sender_id())
        if len(tmp_user_info["card"]) > 0:
            this_msg["Nickname"] = tmp_user_info["card"]
        this_msg["Content"] = str(event.get_message_outline())
        his[group_id].add(this_msg)
        print("add message:", this_msg)
        # dbg_msg_1 , dbg_msg_2 = his[group_id].get_all()
        # print("all message:" , dbg_msg_1 , dbg_msg_2)
        print(dc[group_id])
        global count_recv
        global count_send
        print("recv and send:" , count_recv , count_send)
        is_failed = 1
        if dc[group_id] <= 0 and count_send == count_recv or event.is_at_or_wake_command:
            dc[group_id] = 2147483647
            provider = self.context.get_using_provider()
            if provider:
                is_failed = 0
        if is_failed == 1:
            global failed_count
            failed_count = failed_count + 1
            yield failed_count
        else:
            count_recv = count_recv + 1
            this_id = count_recv
            # if count_send != this_id -1:
            #    print("Skipped!")
            #    count_send = count_send + 1
            #    failed_count = failed_count + 1
            #    yield failed_count
            #    return
            while count_send < this_id - 1:
                await asyncio.sleep(0.1)
            prompt_empty = " "
            his_old , his_new = his[group_id].get_all()
            his_all = "以下是旧聊天记录：\n------\n" + his_old + "\n------\n"
            his_all = his_all + "以下是新聊天记录：\n------\n" + his_new + "\n------\n"
            prom = his_all + CHAT_PROMPT
            # response = await provider.text_chat(prompt = prompt_empty, session_id = event.session_id)
            response = await provider.text_chat(prompt = prom , session_id = None , system_prompt = SYSTEM_PROMPT, func_tool = func_call_inst)
            print(response.completion_text) # LLM 返回的结果
            real_time_new = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            this_msg_self = dict()
            this_msg_self["Time"] = real_time_new
            this_msg_self["User_ID"] = str("514641773")
            this_msg_self["Name"] = str("草莓鲜奶")
            tmp_user_info = await get_user_in_group_info(obj = self, group_id = event.message_obj.group_id, user_id = "514641773")
            if len(tmp_user_info["card"]) > 0:
                this_msg_self["Nickname"] = tmp_user_info["card"]
            this_msg["Content"] = str(response.completion_text)
            his[group_id].add(this_msg_self)
            print("add message Self:", this_msg_self)
            his[group_id].add(this_msg)
            his[group_id].refresh()
            save_config()
            yield event.plain_result(str(response.completion_text)) # 发送一条纯文本消息
            count_send = count_send + 1
            if count_recv == count_send:
                dc[group_id] = random.randint(3,8)
            
# qwq