import logging
import re
import json
import urllib.parse
from app.services.parser.base_parser import BaseParser
from app.utils.logger import logger

class YoutubeParser(BaseParser):
    def __init__(self, real_url):
        super().__init__(real_url)
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.post_data = self._fetch_post_data()

    def _fetch_post_data(self):
        try:
            resp = self.session.get(self.real_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', resp.text)
                if match:
                    player_res = json.loads(match.group(1))
                    return player_res
        except Exception as e:
            logger.warning(f"Youtube raw fetch failed: {e}")
            
        return {}


    def get_real_video_url(self):
        try:
            streamingData = self.post_data.get('streamingData', {})
            formats = streamingData.get('formats', [])
            
            for fmt in formats:
                url = fmt.get('url')
                if url:
                    return url
                    
            for fmt in formats:
                 s_cipher = fmt.get('signatureCipher')
                 if s_cipher:
                     return self._fallback_ytdlp_url()
                     
        except Exception as e:
            logger.warning(f"Youtube URL extraction error: {e}")
            
        return self._fallback_ytdlp_url()
        
    def _fallback_ytdlp_url(self):
        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': False,
                'nocheckcertificate': True,
                'format': 'best[ext=mp4]',
                'extractor_args': {'youtube': {'player_client': ['web_creator', 'web']}},
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.real_url, download=False)
                return info.get('url')
        except Exception as e:
             logger.warning(f"yt-dlp fallback failed: {e}")
        return None

    def get_title_content(self):
        details = self.post_data.get('videoDetails', {})
        title = details.get('title', '')
        desc = details.get('shortDescription', '')
        if desc:
            return f"{title}\n{desc[:200]}"
        return title

    def get_cover_photo_url(self):
        try:
            thumbnails = self.post_data.get('videoDetails', {}).get('thumbnail', {}).get('thumbnails', [])
            if thumbnails:
                return thumbnails[-1].get('url')
        except:
             pass
        return None

    def get_image_list(self):
        return []

    def get_author_info(self):
        details = self.post_data.get('videoDetails', {})
        author_name = details.get('author', '')
        channel_id = details.get('channelId', '')
        
        avatar = None
        try:
             micro = self.post_data.get('microformat', {}).get('playerMicroformatRenderer', {})
             avatar = micro.get('ownerProfileUrl', '') 
        except:
             pass
             
        return {
            "nickname": author_name,
            "author_id": channel_id,
            "avatar": avatar
        }
