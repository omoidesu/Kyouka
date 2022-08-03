import aiohttp

from app.config.common import settings
from app.music.migu.details import get_music_url
from app.music.migu.music import MiguMusic

async def msearch_music_by_keyword(music_name) -> list[MiguMusic]:
    ret = None
    params = {
        'keyword': music_name
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(settings.migu_api + 'search', params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status))
    
    if resp_json.get('result') != 100:
        raise Exception('result: ' + str(resp_json.get('result')))
    else:
        data = resp_json.get('data', {})
        try:
            _ = data.get('total', 0)
        except:
            raise Exception(f"没有搜索到歌曲: {music_name} 哦，试试搜索其他歌曲吧")
        else:
            songlist = data.get('list', [])
            ret = await get_music_url([MiguMusic(**song) for song in songlist])

    return ret[:5] if len(ret) > 5 else ret
