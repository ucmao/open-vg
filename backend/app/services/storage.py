"""Cloudflare R2 storage service or local storage for testing."""
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import os
import shutil
from dotenv import load_dotenv
from typing import Optional, BinaryIO
from io import BytesIO
import mimetypes
from datetime import datetime
import uuid
import secrets
import string
import re

from ..utils.logger import logger

load_dotenv()

# R2 Configuration
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_DOMAIN = os.getenv("R2_PUBLIC_DOMAIN") or os.getenv("STORAGE_CDN_URL")

# App Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class StorageService:
    """Service for managing file uploads to Cloudflare R2 or Local Storage."""
    
    def __init__(self):
        self.is_local = False
        self.is_mock = False
        
        # Check if R2 is configured
        if not all([R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET_NAME]):
            logger.info("R2 configuration is incomplete. Using LOCAL storage mode.")
            self.is_local = True
            return

        # Initialize S3 client for R2/OSS
        try:
            # Use standard S3 virtual hosted style
            s3_config = Config(
                signature_version='s3v4',
                s3={'addressing_style': 'virtual'}
            )
            
            # Auto-detect region from Aliyun endpoint
            region = 'auto'
            endpoint_clean = R2_ENDPOINT.replace('https://', '').replace('http://', '')
            
            # More robust region extraction
            if 'oss-' in endpoint_clean:
                # Find the part that looks like oss-cn-beijing
                parts = endpoint_clean.split('.')
                for p in parts:
                    if p.startswith('oss-'):
                        region = p.replace('oss-', '', 1)
                        break
            
            # Use the base regional endpoint directly. 
            endpoint_url = R2_ENDPOINT if R2_ENDPOINT.startswith('http') else f"https://{R2_ENDPOINT}"
            
            logger.info(f"Connecting to Aliyun OSS at {endpoint_url} (Region: {region}, Style: virtual)")
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                config=s3_config,
                region_name=region
            )
            self.bucket_name = R2_BUCKET_NAME
            self.public_domain = R2_PUBLIC_DOMAIN
        except Exception as e:
            logger.error(f"Failed to initialize R2 client: {e}. Falling back to LOCAL mode.")
            self.is_local = True
    
    def upload_file(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
        public: bool = False
    ) -> str:
        """
        Upload a file to OSS or Local Storage.
        """
        # Ensure we have the data
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        file_data = file_obj.read()

        if self.is_local:
            return self._save_locally(BytesIO(file_data), key)

        try:
            if not content_type:
                content_type, _ = mimetypes.guess_type(key)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            extra_args = {'ContentType': content_type}
            # Note: Aliyun OSS S3 API might not support standard S3 ACLs depending on setup
            # If you get 'AccessDenied' here, it might be due to this line
            # extra_args['ACL'] = 'public-read' if public else 'private'
            
            # Use BytesIO to avoid closing the original file_obj
            temp_obj = BytesIO(file_data)
            self.s3_client.upload_fileobj(
                temp_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            # Generate the final URL
            #  CDN （）， public
            if self.public_domain:
                url = f"{self.public_domain}/{key}"
            else:
                # Use standard R2/OSS URL format: https://bucket.endpoint/key
                endpoint_host = R2_ENDPOINT.replace('https://', '').replace('http://', '')
                protocol = 'https' if R2_ENDPOINT.startswith('https') else 'http'
                url = f"{protocol}://{self.bucket_name}.{endpoint_host}/{key}"
            
            logger.info(f"File uploaded successfully to OSS: {key}")
            return url
            
        except Exception as e:
            # ，
            logger.error(f"❌ OSS Upload Detailed Error: {type(e).__name__} - {str(e)}")
            return self._save_locally(BytesIO(file_data), key)

    def _save_locally(self, file_obj: BinaryIO, key: str) -> str:
        """Helper to save file to local static directory."""
        try:
            local_path = os.path.join("static", key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
                
            with open(local_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)
            
            logger.info(f"File saved locally: {local_path}")
            return f"{BACKEND_URL}/static/{key}"
        except Exception as e:
            logger.error(f"Local save failed: {str(e)}")
            raise

    def upload_file_from_path(
        self,
        file_path: str,
        key: str,
        content_type: Optional[str] = None,
        public: bool = False
    ) -> str:
        try:
            with open(file_path, 'rb') as f:
                return self.upload_file(f, key, content_type, public)
        except Exception as e:
            logger.error(f"Failed to upload file from path: {str(e)}")
            raise
    
    def get_public_url(self, key: str) -> str:
        """
        Get a clean public URL for a file (no signing).
        Supports both local URLs and OSS keys.
        """
        if not key:
            return ""
            
        # 1. If it's already a full local URL, return it as is
        if "localhost" in key or "/static/" in key:
            return key
            
        # 2. If it's an external full URL, check if it's our R2/OSS URL
        if key.startswith('http'):
            # If it's already using our CDN domain, return as is
            if self.public_domain and self.public_domain in key:
                return key
            
            # If it's our R2/OSS endpoint, convert to CDN domain (if configured)
            is_ours = False
            if R2_ENDPOINT:
                endpoint_host = R2_ENDPOINT.replace('https://', '').replace('http://', '')
                if endpoint_host in key or f"{self.bucket_name}.{endpoint_host}" in key:
                    is_ours = True
            
            # If it's our OSS URL and we have CDN domain, convert it
            if is_ours and self.public_domain:
                # Extract the key from the URL
                url_path = key.replace('https://', '').replace('http://', '')
                if '/' in url_path:
                    # Remove bucket name if present
                    remaining = '/'.join(url_path.split('/')[1:])
                    remaining = remaining.split('?')[0]  # Remove query params
                    if remaining.startswith(f"{self.bucket_name}/"):
                        remaining = remaining.replace(f"{self.bucket_name}/", "", 1)
                    return f"{self.public_domain}/{remaining}"
            
            # If it's not our OSS, return as is (external link)
            if not is_ours:
                return key

        # 3. If we are in local mode
        if self.is_local:
            if key.startswith('http'):
                return key
            return f"{BACKEND_URL}/static/{key}"

        # 4. Handle OSS URL construction for keys
        clean_key = key
        if key.startswith('http'):
            # Extract key from existing URL if needed
            url_path = key.replace('https://', '').replace('http://', '')
            if '/' in url_path:
                remaining = '/'.join(url_path.split('/')[1:])
                remaining = remaining.split('?')[0]
                if remaining.startswith(f"{self.bucket_name}/"):
                    clean_key = remaining.replace(f"{self.bucket_name}/", "", 1)
                else:
                    clean_key = remaining
        
        # 5.  key  canonical （ _thumb.webp  _compressed.mp4）， key
        # R2 ：{storage_key}.webp  {storage_key}.mp4
        #  URL  canonical ：{storage_key}-{title}_thumb.webp  {storage_key}-{title}_compressed.mp4
        if clean_key.endswith('_thumb.webp'):
            #  canonical  28  ID + .webp
            # ：{28ID}-{title}_thumb.webp -> {28ID}.webp
            import re
            match = re.match(r'^([A-Za-z0-9]{28})(-.*)?_thumb\.webp$', clean_key)
            if match:
                clean_key = f"{match.group(1)}.webp"
        elif clean_key.endswith('_compressed.mp4'):
            #  canonical  28  ID + .mp4
            # ：{28ID}-{title}_compressed.mp4 -> {28ID}.mp4
            import re
            match = re.match(r'^([A-Za-z0-9]{28})(-.*)?_compressed\.mp4$', clean_key)
            if match:
                clean_key = f"{match.group(1)}.mp4"

        if self.public_domain:
            return f"{self.public_domain}/{clean_key}"
        
        # Standard Aliyun OSS URL format: https://bucket.endpoint/key
        endpoint_host = R2_ENDPOINT.replace('https://', '').replace('http://', '')
        protocol = 'https' if R2_ENDPOINT.startswith('https') else 'http'
        return f"{protocol}://{self.bucket_name}.{endpoint_host}/{clean_key}"

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for a private file.
        Correctly handles both local URLs and OSS keys.
        """
        # If bucket is public read, we don't need to sign
        # For Aliyun OSS, usually we just use the public URL
        # You can toggle this behavior based on your security needs
        return self.get_public_url(key)
    
    def delete_file(self, key: str) -> bool:
        if self.is_local:
            local_path = os.path.join("static", key)
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    def copy_file(self, source_key: str, dest_key: str) -> bool:
        if self.is_local:
            source_path = os.path.join("static", source_key)
            dest_path = os.path.join("static", dest_key)
            if os.path.exists(source_path):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(source_path, dest_path)
                return True
            return False

        try:
            copy_source = {'Bucket': self.bucket_name, 'Key': source_key}
            self.s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=dest_key)
            return True
        except Exception:
            return False
    
    def file_exists(self, key: str) -> bool:
        if self.is_local:
            return os.path.exists(os.path.join("static", key))
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_key(user_identifier: str = None, filename: str = None, prefix: str = None) -> str:
        """
        Generate a flat, unique key using 28-character random alphanumeric string.
        
        Args:
            user_identifier: Deprecated (kept for compatibility)
            filename: Filename, used to extract extension
            prefix: Deprecated (kept for compatibility)
        
        Returns:
            28-character random string + extension
        """
        # 28 （）
        alphabet = string.ascii_letters + string.digits
        short_id = ''.join(secrets.choice(alphabet) for _ in range(28))
        
        #  ID
        if not short_id or len(short_id) != 28:
            logger.warning(f"Generated ID has unexpected format: {short_id}, regenerating...")
            short_id = ''.join(secrets.choice(alphabet) for _ in range(28))
        
        # （， URL ）
        if filename:
            #  filename  URL，
            if filename.startswith('http'):
                filename = filename.split('/')[-1].split('?')[0]
            ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        else:
            ext = 'jpg'
        
        #
        ext = ext.lower()
        if len(ext) > 5 or not ext.isalnum():
            ext = 'jpg'
        
        # ：ID +
        return f"{short_id}.{ext}"
    
    @staticmethod
    def generate_canonical_url(storage_key: str, title: str, file_ext: str = "jpg") -> str:
        """
        Generate a canonical (SEO-friendly) URL for a file.
        
        Format: {PUBLIC_DOMAIN}/{storage_key}-{title_slug}.{ext}
        
        Args:
            storage_key: The storage key (e.g., "9kg03zfbcmucrfamc3epkxz4fkhv")
            title: The title to slugify
            file_ext: File extension (default: "jpg")
        
        Returns:
            Canonical URL string
        """
        # Extract extension from storage_key if present
        if '.' in storage_key:
            storage_key_clean = storage_key.split('.')[0]
        else:
            storage_key_clean = storage_key
        
        # Slugify title: lowercase, replace spaces with hyphens, remove special chars
        if not title:
            title_slug = ""
        else:
            # Convert to lowercase
            title_slug = title.lower()
            # Replace spaces and underscores with hyphens
            title_slug = re.sub(r'[_\s]+', '-', title_slug)
            # Remove all characters that are not alphanumeric or hyphens
            title_slug = re.sub(r'[^a-z0-9\-]', '', title_slug)
            # Remove multiple consecutive hyphens
            title_slug = re.sub(r'-+', '-', title_slug)
            # Remove leading/trailing hyphens
            title_slug = title_slug.strip('-')
            # Limit length to 100 characters
            if len(title_slug) > 100:
                title_slug = title_slug[:100]
        
        # Clean extension
        ext = file_ext.lower()
        if len(ext) > 5 or not ext.isalnum():
            ext = 'jpg'
        
        # Build canonical URL
        public_domain = R2_PUBLIC_DOMAIN or os.getenv("STORAGE_CDN_URL")
        if public_domain:
            domain = public_domain.rstrip('/')
            if title_slug:
                return f"{domain}/{storage_key_clean}-{title_slug}.{ext}"
            else:
                return f"{domain}/{storage_key_clean}.{ext}"
        else:
            # Fallback to local static URL if no public domain configured
            base_url = BACKEND_URL.rstrip('/')
            if title_slug:
                return f"{base_url}/static/{storage_key_clean}-{title_slug}.{ext}"
            else:
                return f"{base_url}/static/{storage_key_clean}.{ext}"

    @staticmethod
    def generate_thumbnail_canonical_url(storage_key: str, title: str, is_video: bool = False) -> str:
        """
        Generate a canonical (SEO-friendly) URL for a thumbnail.
        
        Format: 
        - Video: {PUBLIC_DOMAIN}/{storage_key}-{title_slug}_compressed.mp4
        - Image: {PUBLIC_DOMAIN}/{storage_key}-{title_slug}_thumb.webp
        
        Args:
            storage_key: The storage key (e.g., "9kg03zfbcmucrfamc3epkxz4fkhv")
            title: The title to slugify
            is_video: Whether this is a video thumbnail (default: False)
        
        Returns:
            Canonical URL string for thumbnail
        """
        # Extract extension from storage_key if present
        if '.' in storage_key:
            storage_key_clean = storage_key.split('.')[0]
        else:
            storage_key_clean = storage_key
        
        # Slugify title: lowercase, replace spaces with hyphens, remove special chars
        if not title:
            title_slug = ""
        else:
            # Convert to lowercase
            title_slug = title.lower()
            # Replace spaces and underscores with hyphens
            title_slug = re.sub(r'[_\s]+', '-', title_slug)
            # Remove all characters that are not alphanumeric or hyphens
            title_slug = re.sub(r'[^a-z0-9\-]', '', title_slug)
            # Remove multiple consecutive hyphens
            title_slug = re.sub(r'-+', '-', title_slug)
            # Remove leading/trailing hyphens
            title_slug = title_slug.strip('-')
            # Limit length to 100 characters
            if len(title_slug) > 100:
                title_slug = title_slug[:100]
        
        # Determine suffix and extension based on type
        if is_video:
            suffix = "_compressed"
            ext = "mp4"
        else:
            suffix = "_thumb"
            ext = "webp"
        
        # Build canonical URL
        public_domain = R2_PUBLIC_DOMAIN or os.getenv("STORAGE_CDN_URL")
        if public_domain:
            domain = public_domain.rstrip('/')
            if title_slug:
                return f"{domain}/{storage_key_clean}-{title_slug}{suffix}.{ext}"
            else:
                return f"{domain}/{storage_key_clean}{suffix}.{ext}"
        else:
            # Fallback to local static URL if no public domain configured
            base_url = BACKEND_URL.rstrip('/')
            if title_slug:
                return f"{base_url}/static/{storage_key_clean}-{title_slug}{suffix}.{ext}"
            else:
                return f"{base_url}/static/{storage_key_clean}{suffix}.{ext}"


# Singleton instance
_storage_service: Optional[StorageService] = None

def get_storage_service() -> StorageService:
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
