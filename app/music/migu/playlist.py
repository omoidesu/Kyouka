import aiohttp

from lxml import etree

from app.music.migu.details import fetch_song_by_cid
from app.music.migu.music import MiguMusic
from app.utils.asset_utils import webp2jpeg
from app.utils.message_utils import update_message_by_bot

async def m_fetch_music_list_by_id(bot, playlist_id: int, msg_id: str, get_all:bool = False):
    song_list = []
    cover_urls = {}

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://music.migu.cn/v3/music/playlist/{playlist_id}') as resp:
            if resp.status != 200:
                raise Exception(resp.status)
    
            html = await resp.text()

        etree_html = etree.HTML(html)
        song_list_element = etree_html.xpath('//*[@id="J_PageSonglist"]/div[2]/*')
        try:
            pages = etree_html.xpath('//*[@class="page"]/*')
            lastpage = int(pages[-2].attrib.get('href').split('=')[1])
        except:
            lastpage = 1
        
        song_list = await get_song_list(bot, etree_html, len(song_list_element))
        if get_all:
            for i in range(2, lastpage+1):
                await update_message_by_bot(bot, msg_id, f'正在导入音乐 第{i}页/共{lastpage}页')
                async with session.get(f'https://music.migu.cn/v3/music/playlist/{playlist_id}?page={i}') as resp:
                    if resp.status != 200:
                        continue
            
                    html = await resp.text()

                etree_html = etree.HTML(html)
                song_list_element = etree_html.xpath('//*[@id="J_PageSonglist"]/div[2]/*')

                song_list += await get_song_list(bot, etree_html, len(song_list_element))

    song_list = song_list if get_all else song_list[:15] if len(song_list) > 15 else song_list
    for song in song_list:
        cover_urls[song.cover_url] = await webp2jpeg(bot, song.cover_url) if not cover_urls.get(song.cover_url) else cover_urls[song.cover_url]

    for song in song_list:
        song.cover_url = cover_urls[song.cover_url]
    return song_list


async def get_song_list(bot, etree_html: etree.HTML, length: int) -> list[MiguMusic]:
    song_list = []
    for i in range(1, length+1):
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

    return song_list
