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
                # prompt_zh="请结合聊天室内的所有聊天记录，特别着重参考最近10条聊天记录，推测并生成一段最有可能迎合其他人话语的回应。请根据这些记录的语气、风格和话题内容，生成符合聊天室整体氛围的回应。确保参考的重点是最近10条聊天记录，但也要适当考虑聊天室内的其他历史内容。如果你认为自己无法参与到当前的话题中，可以另开起一个话题，例如：“你们今天都吃了什么？”无需为此回答添加任何额外的修饰词。"
                prompt_en="Please consider all the chat records in the chatroom, with particular emphasis on the most recent 10 messages, and generate a response that is most likely to align with what others would say. Base your response on the tone, style, and topics of these messages, ensuring that it fits the overall atmosphere of the chatroom. Make sure the focus is on the recent 10 messages, but also take into account other historical messages from the chatroom as needed. If you think you cannot participate in the current topic, feel free to introduce a new topic, such as: \"What did you all eat today?\" Do not add any extra embellishments to this response."
                response = await provider.text_chat(prompt=prompt_en, session_id=event.session_id,contexts=None)
                print(response.completion_text) # LLM 返回的结果
                yield event.plain_result(response.completion_text) # 发送一条纯文本消息