import aiohttp

from app.config.common import settings
from app.music.migu.music import MiguMusic
from app.utils.asset_utils import webp2jpeg

bitrate = {0: '128', 1: '320', 2: 'flac'}

async def get_music_url(songs: list[MiguMusic]) -> dict:
    async with aiohttp.ClientSession() as session:
        for song in songs:
            params = {
                'cid': song.music_id
            }
        
            async with session.get(settings.migu_api + 'song', params=params) as resp:
                resp_json = await resp.json()
                if resp.status != 200:
                    raise Exception(str(resp.status))
            
            if resp_json.get('result') != 100:
                raise Exception('result: ' + str(resp_json.get('result')))
            else:
                data = resp_json.get('data', {})
                if data:
                    song.source = data.get(bitrate[settings.migu_bitrate], data.get('128', ''))
                    song.duration = int(data.get('duration', 240) * 1e3)

    return songs


async def fetch_song_by_cid(bot, cid: int, album_name) -> MiguMusic:
    async with aiohttp.ClientSession() as session:
        params = {
            'cid': cid
        }
    
        async with session.get(settings.migu_api + 'song', params=params) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(resp.status))
        
        if resp_json.get('result') != 100:
            raise Exception('result: ' + str(resp_json.get('result')))
        else:
            data = resp_json.get('data', {})
            if not data:
                return None

            data['album'] = {
                'name': album_name,
                'picUrl': data.get('picUrl', '')
            }

            song = MiguMusic(**data)
            song.source = data.get(bitrate[settings.migu_bitrate], data.get('128', ''))
            song.duration = int(data.get('duration', 240) * 1e3)

            song.cover_url = await webp2jpeg(bot, song.cover_url)

            return song
