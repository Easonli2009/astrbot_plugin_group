from astrbot.api.all import *
import random
import time
import json

MAX_HISTORY_COUNT = 5000

class chat_history:
    def __init__(self):
        self.history = []
        self.history_new = []
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

def save_config():
    info_json = json.dumps(his, sort_keys = False, indent = 4, separators = (",", ":"))
    file_save = open("group_config.json", "w")
    file_save.write(info_json)

def read_config():
    file_read = open("group_config.json", "r")
    global his
    his = json.load(file_read)

@register("group", "Lyz09", "我的插件", "1.0.5")
class MyPlugin(Star):
    def __init__(self, context : Context):
        super().__init__(context)
        # read_config()

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器
    async def on_message(self,event : AstrMessageEvent):
        event.stop_event() # 停止事件传播（最新版会报错！！）
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
        if group_id not in his:
            his[group_id] = chat_history()
        dc[group_id] = int(dc.get(group_id)) - 1
        add_str = real_time + " ["+str(event.message_obj.sender.nickname) + "("+str(event.message_obj.sender.user_id) + ")]: " + str(event.get_message_outline())
        his[group_id].add(add_str)
        print("add message:" + add_str)
        dbg_msg_1 , dbg_msg_2 = his[group_id].get_all()
        print("all message:" , dbg_msg_1 , dbg_msg_2)
        print(dc[group_id])
        global count_recv
        global count_send
        print("recv and send:" , count_recv , count_send)
        if count_recv == count_send:
            if dc[group_id] <= 0 or event.is_at_or_wake_command:
                dc[group_id] = random.randint(3,8)
                provider = self.context.get_using_provider()
                if provider:
                    count_recv = count_recv + 1
                    prompt_empty = " "
                    his_old , his_new = his[group_id].get_all()
                    his_all = "以下是旧聊天记录：\n------\n" + his_old + "------\n"
                    his_all = his_all + "以下是新聊天记录：\n------\n" + his_new + "------\n"
                    prom = his_all + "你是一个群聊内的成员，以上是你所在的群聊的聊天记录，你是其中的“草莓鲜奶(id:514641773)”，根据新聊天记录回答你认为最合适用于接下来发表的话语，旧聊天记录用于获取聊天背景。注意：无需为此回答添加任何额外形容词，无需模拟给出的消息格式。"
                    sys_prompt = "你是一名中国广东省广州市的18岁女生，对他人自称“小玲”，你的网名叫“草莓鲜奶”，你没有除了QQ以外的其他平台的账号，现在仍在进行学业。你比较喜欢英语，你的数学和物理不是很好。你的性格较为内向、温和、可爱，一次回答不会暴露自己较多的信息，语气一般较为平淡。你回答的每一句话要尽量简短，且口语化。你可以适当模仿他人的说话风格。你不能让他人发现你是AI，如果有他人向你询问这一方面的话题，请回避。你的每一次回答都要体现上述要求，请牢记。You are currently in a chat room. Based on the chat history, identify the topic that the chat room is currently focused on and respond to that topic with your own answer. Note: You do not need to directly answer the topic you identified. Your response should blend in with the atmosphere of the chat room and should be as conversational as possible. Do not add any embellishments to your answer."
                    # response = await provider.text_chat(prompt = prompt_empty, session_id = event.session_id)
                    response = await provider.text_chat(prompt = prom , session_id = None , system_prompt = sys_prompt)
                    print(response.completion_text) # LLM 返回的结果
                    real_time_new = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                    add_str_new = real_time_new + " ["+str("草莓鲜奶") + "(id:"+str(514641773) + ")]: " + str(response.completion_text)
                    print("add message self:" + add_str_new)
                    his[group_id].add(add_str_new)
                    his[group_id].refresh()
                    # save_config()
                    yield event.plain_result(response.completion_text) # 发送一条纯文本消息
                    count_send = count_send + 1