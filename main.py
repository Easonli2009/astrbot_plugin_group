from astrbot.api.all import *

@register("helloworld", "Lyz09", "我的插件", "1.0.2")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @event_message_type(EventMessageType.PRIVATE_MESSAGE) #过滤私聊消息
    async def on_private_message(self, event: AstrMessageEvent):
        yield event.plain_result("我不理你！")
    
    @event_message_type(EventMessageType.GROUP_MESSAGE) #过滤群聊消息
    async def on_private_message(self, event: AstrMessageEvent):
        yield event.plain_result("我不理你！！")