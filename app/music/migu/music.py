from app.music.music import Music

class MiguMusic(Music):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '未知')
        self.music_id = kwargs.get('cid', -1)
        self.album = kwargs.get('album', {}).get('name', '未知专辑')
        self.cover_url = kwargs.get('album', {}).get('picUrl', '')
        self.author = kwargs.get('artists', [{}])[0].get('name', '未知歌手')
        self.website = 'migu'
