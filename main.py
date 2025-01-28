from astrbot.api.all import *
import random

dc = dict(test="Test")

@register("group", "Lyz09", "我的插件", "1.0.5")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @command("test")
    async def test(self, event: AstrMessageEvent):
        provider = self.context.get_using_provider()
        if provider:
            response = await provider.text_chat("你好", session_id=event.session_id)
            print(response.completion_text) # LLM 返回的结果

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器
    async def on_message(self, event: AstrMessageEvent):
        print("#Debug Message: ")
        print(event.message_obj.raw_message) # 打印消息内容
        group_id=event.get_group_id()
        print("#group id="+group_id)
        global dc
        if group_id not in dc:
            dc[group_id]=random.randint(2,7)
        dc[group_id] = int(dc.get(group_id))-1
        if dc[group_id]<=0:
            dc[group_id]=random.randint(2,7)
            provider = self.context.get_using_provider()
            if provider:
                prompt_en="You are currently in a chat room. Based on the chat history, identify the topic that the chat room is currently focused on and respond to that topic with your own answer. Note: You do not need to directly answer the topic you identified. Your response should blend in with the atmosphere of the chat room and should be as conversational as possible. Do not add any embellishments to your answer."
                response = await provider.text_chat(prompt=prompt_en, session_id=event.session_id,contexts=None)
                print(response.completion_text) # LLM 返回的结果
                yield event.plain_result(response.completion_text) # 发送一条纯文本消息