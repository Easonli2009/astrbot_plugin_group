from astrbot.api.all import *

@register("helloworld", "Lyz09", "让BOT成为活跃于群内的QQ人", "1.0.1")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @event_message_type(EventMessageType.PRIVATE_MESSAGE) #过滤私聊消息
    async def on_private_message(self, event: AstrMessageEvent):
        yield event.plain_result("收到了一条私聊消息。")