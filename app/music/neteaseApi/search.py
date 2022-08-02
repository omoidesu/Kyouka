import aiohttp

from app.config.common import settings
from app.music.music import Music
from app.music.neteaseApi.details import get_mp3_urls
from app.music.neteaseApi.album import get_album_info


async def search_music_by_keyword(music_name: str, limit: int = 10) -> list[Music]:
    url = settings.netease_api + 'search'
    ret = None
    params = {
        'keywords': music_name,
        'limit': limit,
        'type': 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status) + resp_json.get('message'))
            
    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    else:
        data = resp_json.get("result", {}).get("songs", [])
        if data:
            mp3_urls = await get_mp3_urls(*[song['id'] for song in data])
            ret = [Music(
                song.get('id'),
                song.get('name'),
                song.get('artists', [{}])[0].get('name', '未知歌手'),
                mp3_urls.get(song.get('id')),
                song.get('duration', 180000),
                song.get('album', {}).get("name", "未知专辑"),
                (await get_album_info(song.get('album', {}).get('id', ''))).cover_url,
                'netease'
            ) if mp3_urls.get(song.get('id')) else None for song in data]

            for i in range(len(ret)-1, -1, -1):
                if not ret[i]:
                    ret.pop(i)

    return ret[:5] if len(ret) > 5 else ret
