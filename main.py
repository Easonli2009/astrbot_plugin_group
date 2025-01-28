from astrbot.api.all import *
import random

class chat_history:
    def __init__(qwq : string):
        self.history = [qwq]
        del self.history[0]
    def add(str : string):
        self.history.append(str)

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
        print("#message=" + str(event.message_obj.message))
        print("#message_real=" + str(event.get_message_outline()))
        global dc
        if group_id not in dc:
            dc[group_id] = random.randint(2,7)
        if group_id not in his:
            his[group_id] = chat_history("default")
        dc[group_id] = int(dc.get(group_id)) - 1
        print(dc[group_id])
        if dc[group_id] <= 0:
            dc[group_id] = random.randint(2,7)
            provider = self.context.get_using_provider()
            if provider:
                prompt_en = "You are currently in a chat room. Based on the chat history, identify the topic that the chat room is currently focused on and respond to that topic with your own answer. Note: You do not need to directly answer the topic you identified. Your response should blend in with the atmosphere of the chat room and should be as conversational as possible. Do not add any embellishments to your answer."
                prompt_empty = " "
                response = await provider.text_chat(prompt = prompt_empty, session_id = event.session_id)
                print(response.completion_text) # LLM 返回的结果
                yield event.plain_result(response.completion_text) # 发送一条纯文本消息