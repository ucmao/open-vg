import os
import requests
from bs4 import BeautifulSoup
from app.utils.logger import logger

class BaseParser:
    def __init__(self, real_url):
        self.real_url = real_url
        self.headers = None
        self.html_content = None
        self.session = requests.Session()

    def get_real_video_url(self):
        raise NotImplementedError

    def get_title_content(self):
        raise NotImplementedError

    def get_cover_photo_url(self):
        raise NotImplementedError

    def get_author_info(self):
        """ (、、ID)"""
        raise NotImplementedError

    def get_audio_url(self):
        """Get audio download URL"""
        return None

    def get_image_list(self):
        return []

    def get_subtitles(self):
        """Get platform native lyrics/subtitles"""
        return None

    def fetch_html_content(self):
        try:
            resp = self.session.get(self.real_url, headers=self.headers, timeout=5)
            resp.raise_for_status()
            self.html_content = resp.text
            return self.html_content
        except requests.RequestException as e:
            logger.error(f"Failed to get the page: {self.real_url}, Error: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching {self.real_url}: {e}")
            return None

    @staticmethod
    def parse_html_data(html_content, pattern):
        if not html_content:
            logger.error("Empty html_content, skip parsing")
            return "{}"
        
        page_obj = BeautifulSoup(html_content, 'lxml')
        script_tags = page_obj.find_all('script')
        for script in script_tags:
            if script.string:
                match = pattern.search(script.string)
                if match:
                    json_data = match.group(1)
                    json_data = json_data.rstrip(';')
                    json_data = json_data.replace('undefined', 'null')
                    return json_data
        logger.error("Video object not found")
