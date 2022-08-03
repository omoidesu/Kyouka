import aiohttp

from lxml import etree

from app.music.migu.details import fetch_song_by_cid

async def m_fetch_music_list_by_id(bot, playlist_id: int, get_all:bool = False):
    song_list = []

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://music.migu.cn/v3/music/playlist/{playlist_id}') as resp:
            if resp.status != 200:
                raise Exception(resp.status)
    
            html = await resp.text()

    etree_html = etree.HTML(html)
    song_list_element = etree_html.xpath('//*[@id="J_PageSonglist"]/div[2]/*')

    for i in range(1, len(song_list_element)+1):
        try:
            cid = etree_html.xpath(f'//*[@id="J_PageSonglist"]/div[2]/div[{i}]/div[2]/@data-cid')[0]
        except:
            continue

        try:
            album = etree_html.xpath(f'//*[@id="J_PageSonglist"]/div[2]/div[{i}]/div[5]/a/text()')[0].replace('《', '').replace('》', '')
        except:
            album = '未知专辑'

        song_list.append(await fetch_song_by_cid(bot, cid, album))
        for i in range(len(song_list)):
            if song_list[i] is None:
                song_list.pop(i)

    return song_list if get_all else song_list[:15] if len(song_list) > 15 else song_list
