import json

from khl import Bot, Message
from khl.card import CardMessage


async def update_message_by_bot(bot: Bot, msg_id: str, content: str):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await bot.client.gate.request(method=method, route=route, json=json)

async def update_cardmessage(bot: Bot, message: Message, content: CardMessage):
    try:
        content_str = json.dumps(content)
        await update_message_by_bot(bot, message.id, content_str)
    except:
        await message.delete()
        await message.ctx.channel.send(content)