import collections

from pydantic import BaseSettings
from typing import List
from datetime import datetime

from app.music.music import Music


class CommonSettings(BaseSettings):
    debug: bool = False

    admin_users: List[str] = []

    file_logger: bool = True

    token: str = ""
    channel: str = ""
    container_name: str = ""
    bot_name: str = "镜华 Kyouka"

    public: bool = False
    kanban: bool = False
    kanban_channel: str = ""

    bot_market_heart_beat: bool = False
    bot_market_uuid: str = ""

    warned_user_list: List[str] = []
    banned_user_list: List[str] = []

    re_prefix_switch: bool = False
    re_prefix_enable: bool = True
    re_prefix_inbegin: bool = True

    played: int = 0   # ms
    playqueue: collections.deque[Music] = collections.deque()
    lock: bool = False
    playing_lyric: dict = {}
    lyric_msgid: str = ''

    candidates_map: dict = {}
    candidates_lock: bool = False

    enable_netease_api: bool = False
    # type
    #   0: anonymous, 1: phone, 2: phone+captcha, 3: email
    netease_api: str = 'http://cloud-music.pl-fe.cn/'
    netease_login_type: int = 0
    netease_login_phone: int = -1
    netease_login_email: str = ''
    netease_login_passwd: str = ''
    netease_cookie: str = ''
    netease_cookie_limit: str = ''
    netease_cookie_lease: datetime = None

    enable_migu_api: bool = False
    migu_api: str = 'http://localhost:3000/'
    # bitrate:
    #   0: 128k, 1: 320k, 2:flac
    migu_bitrate: int = 0

    class Config:
        env_file = ".env"


settings = CommonSettings()
