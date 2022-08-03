import aiohttp

from app.config.common import settings
from app.music.migu.details import get_music_url
from app.music.migu.music import MiguMusic

async def m_fetch_album_by_id(album_id):
    ret = None
    params = {
        'id': album_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(settings.migu_api + 'album', params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status))
    
    if resp_json.get('result') != 100:
        raise Exception('result: ' + str(resp_json.get('result')))
    else:
        data = resp_json.get('data', {})
        cover_url = 'https:' + data.get('picUrl', '')
        songlist = data.get('songList', [{}])
        for song in songlist:
            song['album']['picUrl'] = cover_url
        ret = await get_music_url([MiguMusic(**song) for song in songlist])

    return ret
