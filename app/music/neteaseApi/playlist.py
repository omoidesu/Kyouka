import aiohttp

from app.config.common import settings
from app.music.music import Music

from app.music.neteaseApi.details import get_mp3_urls
from app.music.neteaseApi.music import NeteaseMusic

async def fetch_music_list_by_id(id: int, get_all: bool = False) -> list[Music]:
    url = settings.netease_api + 'playlist/track/all'
    params = {
        'id': id
    }
    headers = {'cookie': settings.netease_cookie}
    if not get_all:
        params['limit'] = 20

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(resp_json)
            
    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    else:
        songs = [NeteaseMusic(**song) for song in resp_json.get('songs', [])]
        mp3_list = await get_mp3_urls(*[song.music_id for song in songs])
        for song in songs:
            song.source = f'https://music.163.com/song/media/outer/url?id={song.music_id}.mp3' if mp3_list.get(song.music_id, None) else None
            song.website = 'netease'

        for i in range(len(songs) -1, -1, -1):
            if not songs[i].source or not songs[i].is_free:
                songs.pop(i)

    return songs if get_all else songs[:10] if len(songs) > 10 else songs
