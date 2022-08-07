import datetime
import traceback
import aiohttp

from loguru import logger
from khl import Bot, Channel, PublicMessage
from khl.card import CardMessage
from app.CardStorage import lyricCard
from app.config.common import settings
from app.utils.channel_utils import update_channel_name_by_bot
from app.utils.playing_utils import set_playing_game_status_by_bot, BUSY_STATUS_GAME_ID, FREE_STATUS_GAME_ID
from app.voice_utils.container_async_handler import container_handler
from app.music.bilibili.search import BPROXY_API
from app.utils.message_utils import update_cardmessage


async def change_music():
    # logger.debug(f"PLAYED: {settings.played}")
    # logger.debug(f"Q: {[str(music) for music in settings.playqueue]}")
    logger.debug(f"LOCK: {settings.lock}")

    settings.lock = True

    try:
        if len(settings.playqueue) == 0:
            settings.played = 0
            settings.lock = False
            return None
        else:
            first_music = settings.playqueue[0]
            if settings.played == 0:
                await container_handler.create_container(first_music.source)

                first_music.endtime = int(datetime.datetime.now().timestamp() * 1000) + first_music.duration

                return None
            else:
                duration = first_music.duration
                if settings.played + 1000 < duration or (settings.played + 1000 > duration and settings.played < duration):
                    return None
                else:
                    settings.playqueue.popleft()
                    settings.played = -1001
                    if len(settings.playqueue) == 0:
                        await container_handler.stop_container()
                        settings.lyric_msgid = ''
                        settings.playing_lyric = {}
                        settings.played = 0
                        settings.lock = False
                        return None
                    else:
                        next_music = settings.playqueue[0]
                        await container_handler.create_container(next_music.source)

                        next_music.endtime = int(datetime.datetime.now().timestamp() * 1000) + next_music.duration

                        return None
    except Exception as e:
        settings.lock = False
        logger.error(f"error occurred in automatically changing music, error msg: {e}, traceback: {traceback.format_exc()}")

async def update_played_time():
    if settings.playqueue:
        logger.debug(f"PLAYED: {settings.played}, music: {settings.playqueue[0]}")
    if settings.lock:
        settings.played += 1000

async def clear_expired_candidates_cache():
    if settings.candidates_lock:
        return None
    else:
        settings.candidates_lock = True
        try:
            now = datetime.datetime.now()

            need_to_clear = []
            for this_user in settings.candidates_map:
                if now >= settings.candidates_map.get(this_user, {}).get("expire", now):
                    need_to_clear.append(this_user)
            
            for user_need_to_clear in need_to_clear:
                settings.candidates_map.pop(user_need_to_clear, None)
                logger.info(f"cache of user: {user_need_to_clear} is removed")
            
            settings.candidates_lock = False
            return None

        except Exception as e:
            settings.candidates_lock = False
            logger.error(f"error occurred in clearing expired candidates cache, error msg: {e}, traceback: {traceback.format_exc()}")

async def keep_bproxy_alive():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BPROXY_API) as r:
                resp_json = await r.json()
                logger.debug(resp_json)
                logger.info("bproxy is alive now")
    except Exception as e:
        logger.error(f"bproxy is not available, error msg: {e}, traceback: {traceback.format_exc()}")
        logger.error("bproxy is not alive now")

async def update_kanban_info(bot: Bot):
    try:
        if settings.kanban:
            status = "空闲" if len(settings.playqueue) == 0 else "繁忙"
            kanban_info = f"{settings.bot_name}: {status}"
            await update_channel_name_by_bot(bot=bot, channel_id=settings.kanban_channel, new_name=kanban_info)
            logger.info(f"kanban info is updated to {kanban_info} successfully")
    except Exception as e:
        logger.error(f"failed to update the kanban info, error msg: {e}, traceback: {traceback.format_exc()}")

async def update_playing_game_status(bot: Bot):
    try:
        game_status_id = FREE_STATUS_GAME_ID if len(settings.playqueue) == 0 else BUSY_STATUS_GAME_ID
        await set_playing_game_status_by_bot(bot=bot, game_id=game_status_id) 
        logger.info(f"playing status is updated to {game_status_id} successfully.(busy is {BUSY_STATUS_GAME_ID}, free is {FREE_STATUS_GAME_ID})")
    except Exception as e:
        logger.error(f"failed to update playing status, error msg: {e}, traceback: {traceback.format_exc()}")

async def keep_bot_market_heart_beat():
    try:
        bot_market_url = "https://bot.gekj.net/api/v1/online.bot"
        
        if not settings.bot_market_heart_beat:
            logger.info(f"bot market heart beat switch is off, nothing happened")
        else:
            headers = {
                "uuid": settings.bot_market_uuid
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(bot_market_url, headers=headers) as r:
                    resp_json = await r.json()
                    code = resp_json.get("code", -1)
                    msg = resp_json.get("msg", "no message received")
                    if code == 0:
                        logger.info(f"keep bot alive at bot market succeed, msg is {msg}")
                    else:
                        logger.error(f"failed to keep bot alive at bot market, msg is : {msg}")

    except Exception as e:
        logger.error(f"failed to keep bot alive at bot market, error msg: {e}, traceback: {traceback.format_exc()}")

async def refresh_netease_api_cookies():
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.netease_api + 'login/refresh', headers={'cookie': settings.netease_cookie}) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception( resp_json.get('msg'))
            
    status = resp_json.get('status', 500)
    if status != 200:
        raise Exception(str(status) + ' ' + resp_json.get("error", "fetch music source failed, unknown reason, please restart this bot"))
    else:
        cookie = resp_json.get('cookie')
        cookie_list = cookie.split(';')
        for cookie_value in cookie_list:
            if 'NMTID=' in cookie_value:
                settings.netease_cookie = settings.netease_cookie + '; ' + cookie_value
                index = cookie_list.index(cookie_value)
                lease = cookie_list[index + 2]
                cookie_lease_datetime = datetime.datetime.strptime(lease, '%a, %d %b %Y %H:%M:%S GMT')
                break

        settings.netease_cookie_lease = cookie_lease_datetime

async def send_lyric(bot):
    if settings.playqueue:
        playtime = settings.played

        if settings.playing_lyric:
            channel: Channel = settings.playing_lyric.get('channel', None)
            lyrics = settings.playing_lyric.get('lyric', '')
            if not channel or not lyrics:
                raise Exception('歌词错误')
            
            lyric = lyrics.get(playtime + 1, '')
            if not lyric:
                return None

            card = CardMessage(lyricCard(settings.playqueue[0], lyric))

            if not settings.lyric_msgid:
                message = await channel.send(card)
                settings.lyric_msgid = message['msg_id']
            else:
                await update_cardmessage(bot, PublicMessage(
                    msg_id=settings.lyric_msgid,
                    _gate_=bot.client.gate,
                    target_id=settings.lyric_channel,
                    extra={'guild_id': '', 'channel_name': '', 'author': {'id': bot.me}}), card)
