from astrbot.api.all import *

a=0

@register("group", "Lyz09", "我的插件", "1.0.2")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @event_message_type(EventMessageType.GROUP_MESSAGE) # 注册一个过滤器，参见下文。
    async def on_message(self, event: AstrMessageEvent):
        print("#Debug Message: ")
        print(event.message_obj.raw_message) # 打印消息内容
        global a
        a = a+1
        print(a)