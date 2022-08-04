from khl import Bot

async def update_message_by_bot(bot: Bot, msg_id: str, content: str):
    method = 'POST'
    route = 'message/update'
    json = {
        'msg_id': msg_id,
        'content': content
    }
    await bot.client.gate.request(method=method, route=route, json=json)