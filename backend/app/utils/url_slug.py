import re
import unicodedata


def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert text to URL-friendly slug.
    
    Examples:
        "AI Generated Artwork!" -> "ai-generated-artwork"
        "" -> "wo-de-zuo-pin"
        "Test & Demo" -> "test-demo"
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove unicode characters and normalize
    text = unicodedata.normalize('NFKD', text)
    
    # Remove non-ASCII characters, keep only letters, digits, spaces, and hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    # Truncate to max_length
    if len(text) > max_length:
        text = text[:max_length].rstrip('-')
    
    return text


def generate_url_slug(short_code: str, title: str = None) -> str:
    """
    Generate URL slug in format: {short_code}-{title-slug}
    
    Args:
        short_code: 11-character short code (e.g., "5UWSKI183_s")
        title: Optional title to append (e.g., "AI Artwork")
        
    Returns:
        URL slug (e.g., "5UWSKI183_s-ai-artwork")
    """
    if not short_code:
        return ""
    
    slug = short_code
    
    if title:
        title_slug = slugify(title, max_length=80)
        if title_slug:
            slug = f"{short_code}-{title_slug}"
    
    return slug


def extract_short_code_from_slug(slug: str) -> str:
    """
    Extract short_code from URL slug.
    
    Args:
        slug: URL slug (e.g., "5UWSKI183_s" or "5UWSKI183_s-ai-artwork")
        
    Returns:
        short_code (e.g., "5UWSKI183_s")
    """
    if not slug:
        return ""
    
    # Short code is always 11 characters, extract first 11 chars or up to first hyphen
    # Handle both formats: "5UWSKI183_s" and "5UWSKI183_s-title"
    if '-' in slug:
        # Extract part before first hyphen (should be 11 chars)
        short_code = slug.split('-')[0]
        # If it's exactly 11 chars, return it; otherwise return the full slug (backward compat)
        if len(short_code) == 11:
            return short_code
        # Otherwise, might be old format or malformed, return as-is
        return slug
    
    # No hyphen, return as-is (should be 11 chars)
    return slug
