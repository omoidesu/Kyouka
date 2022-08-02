from app.music.music import Music

class NeteaseMusic(Music):
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get('name', '未知')
        self.music_id = kwargs.get('id', '')
        self.author = kwargs.get('ar', [{}])[0].get('name', '未知歌手')
        self.album = kwargs.get('al', {}).get('name', '未知专辑')
        cover_url = kwargs.get('al', {}).get('picUrl', '')
        self.cover_url = cover_url + '?param=130y130' if cover_url else 'https://img.kookapp.cn/assets/2022-07/2rM6IYtAu53uw3uw.png'
        self.duration = kwargs.get('dt', 180000)
        self.is_free: bool = True if kwargs.get('fee', 2) == 0 or kwargs.get('fee', 2) == 8 else False
