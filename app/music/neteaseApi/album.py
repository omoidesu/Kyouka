from dataclasses import dataclass

import aiohttp

from app.config.common import settings
from app.music.neteaseApi.details import get_mp3_urls
from app.music.neteaseApi.music import NeteaseMusic


@dataclass
class Album:
    cover_url: str
    artist: str
    music: list[int]


async def get_album_info(id: int) -> Album:
    url = settings.netease_api + 'album'
    params = {
        'id': id
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                raise Exception(str(resp.status) + resp_json.get('message'))
            resp_json = await resp.json()

    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    else:
        cover = resp_json.get('album', {}).get('picUrl', '')
        if cover:
            cover += '?param=130y130'
        artist = resp_json.get('album', {}).get('artist', {}).get('name', '未知歌手')
        music = [NeteaseMusic(**song) for song in resp_json.get('songs', [])]
        return Album(cover, artist, music)


async def fetch_album_by_id(id: int) ->list[NeteaseMusic]:
    album_info: Album = await get_album_info(id)
    ret: list[NeteaseMusic] = [music for music in album_info.music]

    mp3_url = await get_mp3_urls(*[music.music_id for music in ret])

    for music in ret:
        music.source = mp3_url.get(music.music_id, None)
        music.website = 'netease'

    for i in range(len(ret)-1, -1, -1):
        if not ret[i].source or not ret[i].is_free:
            ret.pop(i)

    return ret
