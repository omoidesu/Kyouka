import aiohttp
import re

from app.config.common import settings
from app.music.music import Music

time_pattern = re.compile('\[(.*?)\]')

async def get_lyric(music: Music) -> dict:
    params = {'id': music}
    lyric_dict = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(settings.netease_api + 'lyric', params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status))

    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    else:
        data = resp_json.get('lrc', {}).get('lyric', '')
        if not data:
            raise Exception('没有找到歌词')

        lyric = data.split('\n')
        for lyric_item in lyric:
            matchObj = time_pattern.search(lyric_item)
            if matchObj:
                match = matchObj.groups()[0]
                if ':' in match and '.' in match:  # [ti: ] [ar: ] etc.
                    time = str_to_sec(match)
                    lyric_str = lyric_item.split(']')[1]
                    lyric_dict[time] = lyric_str
    
    return lyric_dict


def str_to_sec(time_str) -> int:
    mins, secs = time_str.split(':')
    sec, msec = secs.split('.')
    mins = int(mins)
    sec = int(sec)
    msec = int(msec)
    ret_sec = mins * 60 + sec + (1 if msec > 75 else 0)
    return ret_sec * 1000
    