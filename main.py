from astrbot.api.all import *
import random
import time

class chat_history:
    def __init__(self):
        self.history = ["qwq"]
        del self.history[0]
    def add(self , sth : str):
        self.history.append(sth)
    def get_all(self):
        result = ""
        for sth in self.history:
            result = result + sth + "\n"
        return result

dc = dict(test="Test")
his = dict(test="Test")

@register("group", "Lyz09", "我的插件", "1.0.5")
class MyPlugin(Star):
    def __init__(self, context : Context):
        super().__init__(context)

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器
    async def on_message(self,event : AstrMessageEvent):
        print("#Debug Message: ")
        print(event.message_obj.raw_message) # 打印消息内容
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
        add_str = real_time + " ["+str(event.message_obj.sender.nickname) + "(id:"+str(event.message_obj.sender.user_id) + ")]: " + str(event.get_message_outline())
        his[group_id].add(add_str)
        print("add message:" + add_str)
        print("all message:" + his[group_id].get_all())
        print(dc[group_id])
        if dc[group_id] <= 0 or event.is_wake_up():
            dc[group_id] = random.randint(2,7)
            provider = self.context.get_using_provider()
            if provider:
                prompt_empty = " "
                prom = his[group_id].get_all()
                prom = prom + "以上是你所在的群聊的历史聊天记录，你是其中的“草莓鲜奶(id:514641773)”，根据这些内容推测群聊内的成员正在围绕讨论的话题，并围绕着这个话题接话。由于你可能在此之前回答过，因此你应当关心的是你的最后一次发言之后的内容。注意：你不应当回答推测围绕话题的过程。无需为此回答添加任何额外形容词。注意不要过度重复一个内容。"
                # response = await provider.text_chat(prompt = prompt_empty, session_id = event.session_id)
                response = await provider.text_chat(prompt = prom , session_id = None)
                print(response.completion_text) # LLM 返回的结果
                real_time_new = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                add_str_new = real_time_new + " ["+str("草莓鲜奶") + "(id:"+str(514641773) + ")]: " + str(response.completion_text)
                print("add message self:" + add_str_new)
                his[group_id].add(add_str_new)
                yield event.plain_result(response.completion_text) # 发送一条纯文本消息
                event.stop_event() # 停止事件传播
        event.stop_event() # 停止事件传播