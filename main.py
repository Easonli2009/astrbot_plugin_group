from astrbot.api.all import *

@register("helloworld", "Lyz09", "我的插件", "1.0.2")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.event_message_type(filter.EventMessageType.All)
    async def on_message_(self, event: AstrMessageEvent):
        #接收所有类型的消息
        print(event.message_str)