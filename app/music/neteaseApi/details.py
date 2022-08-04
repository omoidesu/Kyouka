import aiohttp

from app.config.common import settings

async def get_mp3_urls(*song_ids: int) -> dict:
    url = settings.netease_api + 'song/url'
    params = {'id': ','.join(map(str, song_ids))}
    headers = {'cookie': settings.netease_cookie}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            resp_json = await resp.json()
            if resp.status != 200:
                return 'search failed, api error'
            
    status = resp_json.get('code', 500)
    if status == 500:
        raise Exception(resp_json.get("error", "fetch music source failed, unknown reason."))
    elif status == -462:
        raise Exception(resp_json.get('message'))
    else:
        data = resp_json.get('data', [])
        if not data:
            raise Exception(resp_json.get('message'))
        return {
            song.get('id'): song.get('url') if song.get('url') and not song.get('freeTrialInfo') else None for song in data
        }
