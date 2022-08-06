import hashlib
import sys

import aiohttp
from app.config.common import settings
from loguru import logger

from datetime import datetime

async def login():
    async with aiohttp.ClientSession() as session:

        '''0: anonimous, 1: phone, 2: phone+captcha, 3: email'''
        if settings.netease_login_type == 0:
            url = settings.netease_api + 'register/anonimous'
            params = None
        elif settings.netease_login_type == 1:
            m = hashlib.md5()
            m.update(settings.netease_login_passwd.encode('utf-8'))
            password_md5 = m.hexdigest()
            url = settings.netease_api + f'login/cellphone'
            params = {
                'phone': str(settings.netease_login_phone),
                'md5_password': password_md5
            }
        elif settings.netease_login_type == 3:
            m = hashlib.md5()
            m.update(settings.netease_login_passwd.encode('utf-8'))
            password_md5 = m.hexdigest()
            url = settings.netease_api + 'login'
            params = {
                'email': settings.netease_login_email,
                'md5_password': password_md5
            }
        elif settings.netease_login_type == 2:
            async with session.get(settings.netease_api + 'captcha/sent', params={'phone': settings.netease_login_phone}) as r:
                if r.status != 200:
                    raise Exception('captcha send failed, api error')
                r_json = await r.json()
                if r_json['code'] == 200:
                    logger.debug('验证码发送成功，请注意查收')
            captcha: str = input('请输入验证码')
            if not captcha.isdigit():
                raise Exception('验证码不合法！')
            url = settings.netease_api + f'login/cellphone'
            params = {
                'phone': str(settings.netease_login_phone),
                'captcha': captcha
            }
    
        async with session.get(url, params=params) as resp:
            login_json = await resp.json()
            if resp.status != 200:
                raise Exception(str(login_json.get('code')) + ' ' + login_json.get('message'))

            status = login_json.get('code', 500)
            if status != 200:
                raise Exception(login_json.get("error", "fetch music source failed, unknown reason."))
            cookies = login_json['cookie']
            settings.netease_cookie, settings.netease_cookie_lease = get_cookie(cookies)
            logger.debug('login success!')


def get_cookie(cookies: str) -> str:
    ret: str = ''
    cookies_list = cookies.split(';')
    cookie_items = []
    cookie_item_list: list = []
    cookie_lease_datetime = datetime.now()
    target_cookie = ['', '', '']
    for c in cookies_list:
        if c:
            if c[0] != ' ':
                if cookie_item_list:
                    cookie_items.append(cookie_item_list)
                    cookie_item_list = []
                cookie_item_list.append(c)
            else:
                cookie_item_list.append(c.strip())

    for cookie_item in cookie_items:
        value = cookie_item[0]
        if 'NMTID=' in value or 'MUSIC_A=' in value or 'MUSIC_U=' in value or '__csrf=' in value:
            # ret = ret + value + '; '
            if 'NMTID' in value:
                logger.debug(value)
                target_cookie[1] = value
            elif 'MUSIC_A' in value:
                logger.debug(value)
                target_cookie[0] = value
            elif '__csrf' in value:
                logger.debug(value)
                target_cookie[2] = value
                cookie_lease = cookie_item[2].split(', ')[1]
                cookie_lease_datetime = datetime.strptime(cookie_lease, r'%d %b %Y %H:%M:%S GMT')
            elif 'MUSIC_U' in value:
                logger.debug(value)
                target_cookie[0] = value
                target_cookie.append('__remember_me=true')

    ret = '; '.join(target_cookie)

    return ret, cookie_lease_datetime.date()
