"""Service for generating thumbnails from images and videos."""
from PIL import Image
import io
import httpx
import subprocess
import os
import tempfile
from typing import Optional

from ..utils.logger import logger


async def download_file(url: str) -> bytes:
    """
    Download a file from URL.
    
    Args:
        url: File URL
        
    Returns:
        File content as bytes
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=60.0)
        response.raise_for_status()
        return response.content


async def generate_image_thumbnail(
    image_url: str,
    max_width: int = 400,
    max_height: int = 400,
    quality: int = 85
) -> bytes:
    """
    Generate a thumbnail from an image URL.
    
    Args:
        image_url: URL of the image
        max_width: Maximum thumbnail width
        max_height: Maximum thumbnail height
        quality: JPEG quality (1-100)
        
    Returns:
        Thumbnail image as bytes
    """
    try:
        # Download image
        image_data = await download_file(image_url)
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        # Generate thumbnail
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        logger.info(f"Thumbnail generated for image: {image_url}")
        return output.read()
        
    except Exception as e:
        logger.error(f"Error generating image thumbnail: {str(e)}")
        raise


async def generate_image_thumbnail_webp(
    image_url: str,
    max_width: int = 800,
    max_height: int = 800,
    quality: int = 85
) -> bytes:
    """
    Generate a WebP thumbnail from an image URL.
    Compress automatically maintaining aspect ratio.
    
    Args:
        image_url: URL of the image
        max_width: Maximum thumbnail width (default: 800)
        max_height: Maximum thumbnail height (default: 800)
        quality: WebP quality 1-100 (default: 85)
        
    Returns:
        Thumbnail image as bytes (WebP format)
    """
    try:
        # Download image
        image_data = await download_file(image_url)
        original_size = len(image_data)
        
        # Open image
        image = Image.open(io.BytesIO(image_data))
        original_width, original_height = image.size
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # ，
        ratio = min(max_width / original_width, max_height / original_height)
        
        if ratio < 1:
            #
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized: {original_width}x{original_height} -> {new_width}x{new_height} (ratio: {ratio:.2f})")
        else:
            # ，
            logger.info(f"Image already small: {original_width}x{original_height}, no resize needed")
        
        # Save to bytes as WebP
        output = io.BytesIO()
        image.save(
            output, 
            format='WEBP', 
            quality=quality, 
            method=6,  #  (0-6, 6)
            optimize=True
        )
        output.seek(0)
        webp_data = output.read()
        webp_size = len(webp_data)
        
        #
        compression_ratio = (1 - webp_size / original_size) * 100 if original_size > 0 else 0
        
        logger.info(
            f"WebP thumbnail generated: {image_url}\n"
            f"  Original: {original_width}x{original_height}, {original_size/1024:.1f}KB\n"
            f"  WebP: {image.size[0]}x{image.size[1]}, {webp_size/1024:.1f}KB\n"
            f"  Compression: {compression_ratio:.1f}% smaller"
        )
        
        return webp_data
        
    except Exception as e:
        logger.error(f"Error generating WebP thumbnail: {str(e)}")
        raise


async def generate_video_thumbnail(
    video_url: str,
    time_position: float = 1.0
) -> Optional[bytes]:
    """
    Generate a thumbnail from a video URL using ffmpeg.
    
    Args:
        video_url: URL of the video
        time_position: Time position in seconds to capture frame
        
    Returns:
        Thumbnail image as bytes or None if failed
    """
    try:
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ffmpeg not found. Cannot generate video thumbnail.")
            return None
        
        # Download video to temp file
        video_data = await download_file(video_url)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file:
            video_file.write(video_data)
            video_path = video_file.name
        
        try:
            # Create temp file for thumbnail
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as thumb_file:
                thumb_path = thumb_file.name
            
            # Extract frame using ffmpeg
            subprocess.run([
                'ffmpeg',
                '-ss', str(time_position),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                '-vf', 'scale=800:-1',  #  800 ，
                thumb_path,
                '-y'
            ], capture_output=True, check=True)
            
            # Read thumbnail
            with open(thumb_path, 'rb') as f:
                thumbnail_data = f.read()
            
            logger.info(f"Video thumbnail generated: {video_url}")
            return thumbnail_data
            
        finally:
            # Clean up temp files
            if os.path.exists(video_path):
                os.unlink(video_path)
            if os.path.exists(thumb_path):
                os.unlink(thumb_path)
        
    except Exception as e:
        logger.error(f"Error generating video thumbnail: {str(e)}")
        return None


async def generate_video_thumbnail_webp(
    video_url: str,
    time_position: float = 1.0,
    max_width: int = 800,
    max_height: int = 800,
    quality: int = 85
) -> Optional[bytes]:
    """
    Generate a WebP thumbnail from a video URL using ffmpeg.
    
    Args:
        video_url: URL of the video
        time_position: Time position in seconds to capture frame
        max_width: Maximum thumbnail width (default: 800)
        max_height: Maximum thumbnail height (default: 800)
        quality: WebP quality 1-100 (default: 85)
        
    Returns:
        Thumbnail image as bytes (WebP format) or None if failed
    """
    try:
        # First generate JPEG thumbnail using ffmpeg
        jpeg_thumbnail = await generate_video_thumbnail(video_url, time_position)
        if not jpeg_thumbnail:
            return None
        
        # Convert JPEG to WebP
        image = Image.open(io.BytesIO(jpeg_thumbnail))
        original_width, original_height = image.size
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        
        # ，
        ratio = min(max_width / original_width, max_height / original_height)
        
        if ratio < 1:
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes as WebP
        output = io.BytesIO()
        image.save(
            output, 
            format='WEBP', 
            quality=quality, 
            method=6,
            optimize=True
        )
        output.seek(0)
        
        logger.info(f"Video WebP thumbnail generated: {video_url} -> {image.size[0]}x{image.size[1]}")
        return output.read()
        
    except Exception as e:
        logger.error(f"Error generating video WebP thumbnail: {str(e)}")
        return None


async def compress_video_h264(
    video_url: str,
    max_height: int = 480,
    crf: int = 23
) -> Optional[bytes]:
    """
    Compress video to H.264 + 480p for thumbnail_url storage.
    
    Args:
        video_url: Original video URL
        max_height: Max height (default 480p)
        crf: Constant Rate Factor (18-28, default 23)
        
    Returns:
        Compressed video bytes or None on failure
    """
    try:
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ffmpeg not found. Cannot compress video.")
            return None
        
        # Download video to temp file
        video_data = await download_file(video_url)
        original_size = len(video_data)
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as video_file:
            video_file.write(video_data)
            input_path = video_file.name
        
        try:
            # Create temp file for compressed video
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as compressed_file:
                output_path = compressed_file.name
            
            #  ffmpeg ：H.264 ，480p
            # -vf scale=-2:480:  480，
            # -c:v libx264:  H.264
            # -crf 23: ，
            # -preset medium: （medium ）
            # -movflags +faststart:
            # -c:a aac:  AAC
            # -b:a 128k:
            result = subprocess.run([
                'ffmpeg',
                '-i', input_path,
                '-vf', f'scale=-2:{max_height}',  # ，
                '-c:v', 'libx264',
                '-crf', str(crf),
                '-preset', 'medium',
                '-movflags', '+faststart',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  #
                output_path
            ], capture_output=True, check=True)
            
            # Read compressed video
            with open(output_path, 'rb') as f:
                compressed_data = f.read()
            
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            logger.info(
                f"Video compressed: {video_url}\n"
                f"  Original: {original_size/1024/1024:.2f}MB\n"
                f"  Compressed: {compressed_size/1024/1024:.2f}MB ({max_height}p)\n"
                f"  Compression: {compression_ratio:.1f}% smaller"
            )
            
            return compressed_data
            
        finally:
            # Clean up temp files
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"FFmpeg compression error: {error_msg}")
        return None
    except Exception as e:
        logger.error(f"Error compressing video: {str(e)}")
        return None

