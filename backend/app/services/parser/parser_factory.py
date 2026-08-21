from app.services.parser.tiktok_parser import TiktokParser
from app.services.parser.youtube_parser import YoutubeParser
from app.services.parser.instagram_parser import InstagramParser
from app.services.parser.twitter_parser import TwitterParser
from urllib.parse import urlparse
from app.utils.logger import logger

class ParserFactory:
    platform_to_parser = {
        "TikTok": TiktokParser,
        "YouTube": YoutubeParser,
        "Instagram": InstagramParser,
        "X": TwitterParser
    }

    @staticmethod
    def get_platform_from_url(url: str) -> str:
        """
        Identify platform based on URL domain
        """
        if not url:
            return None
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if "tiktok.com" in domain:
                return "TikTok"
            elif "youtube.com" in domain or "youtu.be" in domain:
                return "YouTube"
            elif "instagram.com" in domain:
                return "Instagram"
            elif "twitter.com" in domain or "x.com" in domain:
                return "X"
        except Exception as e:
            logger.error(f"Error parsing URL domain: {e}")
        return None

    @staticmethod
    def parse_url(url: str):
        """
        Identify platform, create parser, and extract all metadata in standard format
        """
        platform = ParserFactory.get_platform_from_url(url)
        if not platform:
            raise ValueError("Unsupported or invalid overseas URL platform")

        parser_class = ParserFactory.platform_to_parser.get(platform)
        parser = parser_class(url)

        title = parser.get_title_content()
        video_url = parser.get_real_video_url()
        cover_url = parser.get_cover_photo_url()
        author = parser.get_author_info()
        images = parser.get_image_list()
        audio_url = parser.get_audio_url()

        return {
            "platform": platform,
            "title": title,
            "video_url": video_url,
            "cover_url": cover_url,
            "author": author,
            "images": images,
            "audio_url": audio_url
        }
