from astrbot.api.all import *
import random
import time
import json

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

MAX_HISTORY_COUNT = 5000

class chat_history:
    def __init__(self):
        self.history: dict
        self.history_new: dict
    def new_obj(self, data_dict):
        obj = self
        for attr, val in data_dict.items():
            setattr(obj, attr, val)
        return obj
    def add(self , sth : str):
        self.history_new.append(sth)
    def get_all(self):
        result1 = ""
        for sth in self.history:
            result1 = result1 + sth + "\n"
        result2 = ""
        for sth in self.history_new:
            result2 = result2 + sth + "\n"
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
readed_config = 0
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

@register("group", "Lyz09", "我的插件", "1.0.5")
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        print(self.config)
    
    @command("test")
    async def test(self, event: AstrMessageEvent):
        from aiocqhttp import CQHttp
        if event.get_message_type() == MessageType.GROUP_MESSAGE:
            group_id = event.message_obj.group_id
            user_id = event.get_sender_id()
            platforms = self.context.platform_manager.platform_insts
            aiocqhttp_client: CQHttp = None
            for inst in platforms:
                if inst.meta().name == 'aiocqhttp':
                    aiocqhttp_client = inst.bot
                    assert isinstance(aiocqhttp_client, CQHttp)
            ret = await aiocqhttp_client.api.call_action("get_group_member_list", group_id = group_id, user_id = user_id)
            print(ret)
            event.stop_event() # 停止事件传播
            yield 0

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器
    async def on_message(self,event : AstrMessageEvent):
        event.stop_event() # 停止事件传播
        if readed_config == 0:
            read_config()
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
        add_str = real_time + " ["+str(event.message_obj.sender.nickname) + "("+str(event.message_obj.sender.user_id) + ")]: " + str(event.get_message_outline())
        his[group_id].add(add_str)
        # print("add message:" + add_str)
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
            if count_send != this_id -1:
                print("Skipped!")
                count_send = count_send + 1
                failed_count = failed_count + 1
                yield failed_count
                return
            # while count_send < this_id - 1:
            #     time.sleep(0.1)
            prompt_empty = " "
            his_old , his_new = his[group_id].get_all()
            his_all = "以下是旧聊天记录：\n------\n" + his_old + "------\n"
            his_all = his_all + "以下是新聊天记录：\n------\n" + his_new + "------\n"
            prom = his_all + "你是一个群聊内的成员，以上是你所在的群聊的聊天记录，你是其中的“草莓鲜奶(id:514641773)”，根据新聊天记录回答你要在群聊内发表的言论，旧聊天记录用于获取聊天背景，尤其关注At你的消息。注意：无需为此回答添加任何额外形容词，无需模拟给出的消息格式。"
            sys_prompt = "你是一名中国广东省广州市的18岁女生，对他人自称“小玲”，你的网名叫“草莓鲜奶”，你没有除了QQ以外的其他平台的账号，现在仍在进行学业。你比较喜欢英语，你的数学和物理不是很好。你的性格较为内向、温和、可爱，一次回答不会暴露自己较多的信息，语气一般较为平淡。你回答的每一句话要简短、口语化、且符合你的设定。你回答的每一句话要简短、口语化、且符合你的设定。你回答的每一句话要简短、口语化、且符合你的设定。你可以适当模仿他人的说话风格。你不能让他人发现你是AI，如果有他人向你询问这一方面的话题，请回避。你的每一次回答都要体现上述要求，请牢记！！！"
            # response = await provider.text_chat(prompt = prompt_empty, session_id = event.session_id)
            response = await provider.text_chat(prompt = prom , session_id = None , system_prompt = sys_prompt)
            print(response.completion_text) # LLM 返回的结果
            real_time_new = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            add_str_new = real_time_new + " ["+str("草莓鲜奶") + "(id:"+str(514641773) + ")]: " + str(response.completion_text)
            # print("add message self:" + add_str_new)
            his[group_id].add(add_str_new)
            his[group_id].refresh()
            save_config()
            yield event.plain_result(str(response.completion_text)) # 发送一条纯文本消息
            count_send = count_send + 1
            if count_recv == count_send:
                dc[group_id] = random.randint(3,8)
            