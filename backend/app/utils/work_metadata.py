"""
Utility functions for generating work metadata (title, description).
"""
import string


def clean_prompt(prompt: str) -> str:
    """
    Clean prompt text by removing newlines and stripping whitespace.
    
    Args:
        prompt: The prompt text
    
    Returns:
        Cleaned prompt text
    """
    return prompt.replace('\n', ' ').strip()


def generate_work_title(prompt: str, max_length: int = 55) -> str:
    """
    Generate work title from prompt.
    
    Title is just the truncated prompt with title case (all words capitalized).
    If prompt exceeds max_length, it will be truncated at the last space
    before max_length and "..." will be appended.
    
    Args:
        prompt: The prompt text
        max_length: Maximum length for title (default: 55)
    
    Returns:
        Truncated prompt text with title case (no model prefix)
    
    Examples:
        >>> generate_work_title("two people walk the bridge")
        'Two People Walk The Bridge'
        >>> generate_work_title("two people walk the bridge under a large cherry blossom tree in spring with pink petals falling")
        'Two People Walk The Bridge Under A Large Cherry Blossom Tree In Spring With Pink...'
    """
    prompt_clean = clean_prompt(prompt)
    
    if len(prompt_clean) > max_length:
        # Truncate at max_length and backtrack to previous space
        truncated = prompt_clean[:max_length].rsplit(' ', 1)[0] + "..."
    else:
        truncated = prompt_clean
    
    # Convert to title case (all words capitalized)
    # Use string.capwords instead of .title() to avoid issues with apostrophes
    # e.g., "Sora's" stays as "Sora's" instead of "Sora'S"
    return string.capwords(truncated)


def generate_work_description(prompt: str, model_name: str, max_length: int = 100) -> str:
    """
    Generate work description from prompt with model name prefix.
    
    Description format: "{ModelName} Prompt: "{truncated_prompt}..." Created with VidGen.
    If prompt exceeds max_length, it will be truncated at the last space
    before max_length. The truncated/complete prompt is wrapped in quotes.
    
    Args:
        prompt: The prompt text
        model_name: The model name to use as prefix
        max_length: Maximum length for description (default: 100)
    
    Returns:
        Description with format: "{ModelName} Prompt: "{truncated_prompt}..." Created with VidGen."
    
    Examples:
        >>> generate_work_description("two people walk the bridge", "Sora")
        'Sora Prompt: "two people walk the bridge..." Created with VidGen.'
        >>> generate_work_description("a very long prompt that exceeds 100 characters and will be truncated at the last space before the limit", "Sora")
        'Sora Prompt: "a very long prompt that exceeds 100 characters and will be truncated at the last space before..." Created with VidGen.'
    """
    prompt_clean = clean_prompt(prompt)
    model_prefix = f"{model_name.capitalize()} Prompt: "
    
    if len(prompt_clean) > max_length:
        # Truncate at max_length and backtrack to previous space
        desc_truncated = prompt_clean[:max_length].rsplit(' ', 1)[0]
    else:
        desc_truncated = prompt_clean
    
    return f'{model_prefix}"{desc_truncated}..." Created with VidGen.'


def generate_work_metadata(prompt: str, model_name: str, 
                           title_max_length: int = 55, 
                           desc_max_length: int = 100) -> tuple[str, str]:
    """
    Generate both title and description for a work.
    
    This is the standard method used in most places:
    - Title: truncated prompt with title case (all words capitalized, no model prefix)
    - Description: "{ModelName} Prompt: "{truncated_prompt}..." Created with VidGen."
    
    Args:
        prompt: The prompt text
        model_name: The model name to use in description
        title_max_length: Maximum length for title (default: 55)
        desc_max_length: Maximum length for description (default: 100)
    
    Returns:
        Tuple of (title, description)
    
    Examples:
        >>> title, desc = generate_work_metadata("A beautiful sunset", "Sora")
        >>> title
        'A Beautiful Sunset'
        >>> desc
        'Sora Prompt: "A beautiful sunset..." Created with VidGen.'
    """
    title = generate_work_title(prompt, title_max_length)
    description = generate_work_description(prompt, model_name, desc_max_length)
    return title, description
