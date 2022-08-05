import aiohttp

from app.config.common import settings
from app.music.music import Music
from app.music.neteaseApi.details import get_mp3_urls

async def fetch_radio_by_id(rid: int, get_all: bool, reverse: bool = False) -> list[Music]:
    ret = None
    url = settings.netease_api + 'dj/program'
    params = {
        'rid': rid
    }
    if not get_all:
        params['limit'] = 10
    if reverse:
        params['asc'] = 'true'

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status) + resp_json.get('message'))
            
    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    else:
        programs = resp_json.get('programs', [])
        mp3_url = await get_mp3_urls(*[program.get('mainSong', {}).get('id', '') for program in programs])

        ret = [Music(
            program.get('mainSong', {}).get('id', ''),
            program.get('mainSong', {}).get('name', '未知节目'),
            program.get('mainSong', {}).get('artists', [{}])[0].get('name', '未知歌手'),
            mp3_url.get(program.get('mainSong', {}).get('id', ''), ''),
            program.get('mainSong', {}).get('duration', '180000'),
            program.get('mainSong', {}).get('album', {}).get('name', '未知专辑'),
            program.get('mainSong', {}).get('album', {}).get('picUrl', ''),
            'netease_radio'
        ) for program in programs]

        for i in range(len(ret)-1, -1, -1):
            if ret[i].cover_url:
                ret[i].cover_url += '?param=130y130'
            if not ret[i].source:
                ret.pop(i)

    return ret
