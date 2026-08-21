import re
import json
import random
from app.services.parser.base_parser import BaseParser
from app.utils.logger import logger

USER_AGENT_PC = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
]

class TiktokParser(BaseParser):
    def __init__(self, real_url):
        super().__init__(real_url)
        self.headers = {
            'User-Agent': random.choice(USER_AGENT_PC),
        }
        self.video_id = self._extract_id()
        self.post_data = self._fetch_post_data()

    def _extract_id(self):
        if not self.real_url:
            return None
            
        match = re.search(r'/video/(\d+)', self.real_url)
        if match:
            return match.group(1)
            
        match = re.search(r'/v/(\d+)', self.real_url)
        if match:
            return match.group(1)
            
        return None

    def _fetch_post_data(self):
        if not self.video_id:
            logger.error("TiktokParser: Could not extract video ID.")
            return {}
            
        url = "https://www.tikwm.com/api/"
        params = {
            'url': self.real_url,
            'count': 12,
            'cursor': 0,
            'web': 1,
            'hd': 1
        }
        try:
            resp = self.session.get(url, params=params, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 0:
                     return data.get('data', {})
        except Exception as e:
            logger.warning(f"Tiktok API fetch failed: {e}")
            
        return {}

    def get_real_video_url(self):
        try:
            play_addr = self.post_data.get('hdplay') or self.post_data.get('play')
            if play_addr:
                if play_addr.startswith('/'):
                     return f"https://www.tikwm.com{play_addr}"
                return play_addr
        except Exception as e:
            logger.warning(f"Failed to extract real video url: {e}")
            
        return None

    def get_title_content(self):
        return self.post_data.get('title', '')

    def get_cover_photo_url(self):
        try:
            cover = self.post_data.get('cover')
            if cover:
                if cover.startswith('/'):
                     return f"https://www.tikwm.com{cover}"
                return cover
        except:
            pass
        return None

    def get_image_list(self):
        images = []
        try:
            if 'images' in self.post_data and isinstance(self.post_data['images'], list):
                for img in self.post_data['images']:
                    images.append(img)
        except:
            pass
        return images

    def get_audio_url(self):
        try:
            music = self.post_data.get('music')
            if music:
                 if music.startswith('/'):
                     return f"https://www.tikwm.com{music}"
                 return music
        except:
            pass
        return None

    def get_author_info(self):
        try:
            author = self.post_data.get('author', {})
            if author:
                uid = author.get('unique_id', '') or author.get('id', '')
                nickname = author.get('nickname', '')
                avatar = author.get('avatar', '')
                if avatar.startswith('/'):
                     avatar = f"https://www.tikwm.com{avatar}"
                
                return {
                    "nickname": nickname,
                    "author_id": str(uid),
                    "avatar": avatar
                }
        except:
            pass
        return None
