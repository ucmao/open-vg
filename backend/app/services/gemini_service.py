"""Service for interacting with Google Gemini API."""
import json
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

from ..utils.logger import logger
from ..models.system_config import SystemConfig
from ..utils.crypto import decrypt_value


class GeminiService:
    """Service for managing Gemini API interactions."""
    
    def __init__(self, db_session=None):
        """
        Initialize Gemini service.
        
        Args:
            db_session: Optional database session. If not provided, will create a new one.
        """
        self.db = db_session
        self._api_key = None
        self._model_name = None
        self._fallback_model_name = None
        self._initialized = False
        self.client = None
    
    def _normalize_model_name(self, model_name: str) -> str:
        """
        Normalize model name by removing 'models/' prefix if present.
        Also handle comma-separated models (use first one as primary).
        
        Args:
            model_name: Raw model name from config
            
        Returns:
            Normalized model name without 'models/' prefix
        """
        if not model_name:
            return model_name
        
        # Handle comma-separated models (use first one)
        if ',' in model_name:
            model_name = model_name.split(',')[0].strip()
        
        # Remove 'models/' prefix if present
        if model_name.startswith('models/'):
            model_name = model_name[7:]  # Remove 'models/' prefix
        
        return model_name.strip()
    
    def _load_config(self):
        """Load configuration from SystemConfig."""
        if self._initialized:
            return
        
        try:
            # Get database session
            if not self.db:
                from ..models.base import get_db
                db_gen = get_db()
                self.db = next(db_gen)
            
            # Get API key
            api_key_config = self.db.query(SystemConfig).filter(
                SystemConfig.config_key == "gemini_api_key"
            ).first()
            
            if not api_key_config or not api_key_config.config_value:
                raise ValueError("Gemini API key not configured. Please configure it in admin panel.")
            
            # Decrypt if needed
            api_key = api_key_config.config_value
            if api_key_config.is_encrypted:
                try:
                    api_key = decrypt_value(api_key)
                except Exception as e:
                    logger.error(f"Failed to decrypt Gemini API key: {e}")
                    raise ValueError("Failed to decrypt Gemini API key. Please check configuration.")
            
            # Get model name (optional, defaults to gemini-1.5-flash)
            model_config = self.db.query(SystemConfig).filter(
                SystemConfig.config_key == "gemini_model"
            ).first()
            
            model_name = "gemini-1.5-flash"  # Default
            if model_config and model_config.config_value:
                model_name = self._normalize_model_name(model_config.config_value.strip())
            
            # Get fallback model name (optional)
            fallback_model_config = self.db.query(SystemConfig).filter(
                SystemConfig.config_key == "gemini_fallback_model"
            ).first()
            
            fallback_model_name = None
            if fallback_model_config and fallback_model_config.config_value:
                fallback_model_name = self._normalize_model_name(fallback_model_config.config_value.strip())
            
            # Initialize Gemini client with new SDK
            self.client = genai.Client(api_key=api_key)
            self._api_key = api_key
            self._model_name = model_name
            self._fallback_model_name = fallback_model_name
            self._initialized = True
            
            logger.info(f"Gemini service initialized with model: {model_name}, fallback: {fallback_model_name or 'None'}")
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini service: {str(e)}")
    
    def generate_seo_content(
        self,
        prompt_content: str
    ) -> Dict[str, Any]:
        """Generate SEO title and description from prompt content."""
        self._load_config()
        
        try:
            system_prompt = """You are an SEO expert. Based on the prompt content provided, help me create:
1. A 60-character SEO title (optimize for moderate search volume, moderate difficulty keywords, in English)
2. A 145-character SEO description (optimize for moderate search volume, moderate difficulty keywords, in English)

Return the result in JSON format:
{
  "title": "SEO title here (exactly 60 characters)",
  "description": "SEO description here (exactly 145 characters)"
}

Important:
- Title must be exactly 60 characters
- Description must be exactly 145 characters
- Use English language
- Focus on keywords with moderate search volume and moderate optimization difficulty
- Make it SEO-friendly and engaging"""
            
            full_prompt = f"""{system_prompt}

Prompt content:
{prompt_content}

Please analyze the prompt content and generate the SEO title and description. Return only valid JSON."""
            
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=512
                )
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate and truncate to exact character limits
            title = result.get("title", "")[:60]
            description = result.get("description", "")[:145]
            
            return {
                "title": title,
                "description": description
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI response. Please try again.")
        except Exception as e:
            logger.error(f"Failed to generate SEO content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to generate SEO content: {str(e)}")
    
    def generate_tags(
        self,
        prompt_content: str
    ) -> List[str]:
        """Generate tags from prompt content."""
        self._load_config()
        
        try:
            system_prompt = """Based on the prompt content provided, help me extract 0-5 tag words that best describe the content.

Return the result in JSON array format:
["tag1", "tag2", "tag3"]

Important:
- Return 0-5 tags maximum
- Each tag should be a single word or short phrase
- Use English
- Return only the JSON array, no other text"""
            
            full_prompt = f"""{system_prompt}

Prompt content:
{prompt_content}

Please analyze the prompt content and extract the most relevant tags. Return only valid JSON array."""
            
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=512
                )
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            tags = json.loads(response_text)
            
            # Validate it's a list and limit to 5 tags
            if not isinstance(tags, list):
                tags = []
            
            # Limit to 5 tags and ensure they're strings
            tags = [str(tag).strip() for tag in tags[:5] if tag]
            
            return tags
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI response. Please try again.")
        except Exception as e:
            logger.error(f"Failed to generate tags: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to generate tags: {str(e)}")
    
    def generate_tags_batch(
        self,
        prompt_contents: List[str],
        max_per_request: int = 10,
        max_prompt_chars: int = 500
    ) -> List[List[str]]:
        """
        Batch generate tags for multiple prompts in a single API call.
        
        Args:
            prompt_contents: Multiple prompt texts
            max_per_request: Max items per request (recommended 5-10)
            max_prompt_chars: Prompt truncation length to save tokens
            
        Returns:
            List of tag lists corresponding 1-to-1 with prompt_contents
        """
        if not prompt_contents:
            return []
        
        self._load_config()
        
        #  prompt， token
        truncated = [
            (p[:max_prompt_chars] + ("..." if len(p) > max_prompt_chars else ""))
            for p in prompt_contents
        ]
        
        prompts_block = "\n\n---\n\n".join(
            f"[Prompt {i+1}]\n{t}" for i, t in enumerate(truncated)
        )
        
        system_prompt = f"""For each of the {len(truncated)} prompts below, extract 0-5 tag words that best describe the content (single word or short phrase, English).

Return a JSON array of arrays: one array per prompt, in the same order.
Example for 2 prompts: [["tag1","tag2"], ["tag3","tag4","tag5"]]

Important:
- Exactly {len(truncated)} inner arrays, one per prompt
- 0-5 tags per prompt, English only
- Return only the JSON array of arrays, no other text"""

        full_prompt = f"""{system_prompt}

{prompts_block}

Return only valid JSON array of {len(truncated)} tag arrays."""

        try:
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=min(1024, 256 + len(truncated) * 80)
                )
            )
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            if not isinstance(result, list):
                result = []
            
            #
            out: List[List[str]] = []
            for i in range(len(prompt_contents)):
                if i < len(result) and isinstance(result[i], list):
                    tags = [str(t).strip() for t in result[i][:5] if t]
                else:
                    tags = []
                out.append(tags)
            return out
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini batch tags JSON: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI batch tags response.")
        except Exception as e:
            logger.error(f"Failed to generate tags batch: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def classify_category(
        self,
        prompt_content: str,
        categories: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Classify prompt content into the most appropriate category."""
        self._load_config()
        
        try:
            # Format categories for the prompt
            level1_categories = []
            level2_categories = []
            
            for cat in categories:
                if cat.get('level') == 1:
                    level1_categories.append(cat.get('category_name', ''))
                elif cat.get('level') == 2:
                    parent_name = None
                    # Find parent name
                    for parent_cat in categories:
                        if parent_cat.get('id') == cat.get('parent_id'):
                            parent_name = parent_cat.get('category_name')
                            break
                    if parent_name:
                        level2_categories.append(f"{parent_name}|{cat.get('category_name', '')}")
            
            categories_text = "Level 1 Categories:\n"
            for cat in level1_categories:
                categories_text += f"- {cat}\n"
            
            if level2_categories:
                categories_text += "\nLevel 2 Categories:\n"
                for cat in level2_categories:
                    categories_text += f"- {cat}\n"
            
            system_prompt = """Based on the prompt content and the provided category list, determine which category is most appropriate.

Return the result in JSON format:
{
  "category": "Level1" or "Level1|Level2"
}

Important:
- Return the category in format "Level1" for level 1 only, or "Level1|Level2" for level 2
- If no category matches well, return null
- Return only valid JSON"""
            
            full_prompt = f"""{system_prompt}

Prompt content:
{prompt_content}

{categories_text}

Please analyze the prompt content and determine the most appropriate category. Return only valid JSON."""
            
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=512
                )
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            category = result.get("category")
            
            # Validate category exists in provided list
            if category:
                if "|" in category:
                    # Level 2 category
                    parts = category.split("|", 1)
                    if parts[0] in level1_categories and category in level2_categories:
                        return category
                else:
                    # Level 1 category
                    if category in level1_categories:
                        return category
            
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI response. Please try again.")
        except Exception as e:
            logger.error(f"Failed to classify category: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to classify category: {str(e)}")
    
    def generate_blog_seo(
        self,
        title: str,
        content: str,
        excerpt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate SEO title, description, tags, and excerpt for a blog post.
        Automatically retries with fallback model if primary model is overloaded.
        
        Args:
            title: Blog post title
            content: Blog post content (HTML or plain text)
            excerpt: Optional excerpt/summary
            
        Returns:
            Dict with 'title', 'description', 'tags', and 'excerpt' keys
        """
        self._load_config()
        
        # Try primary model first, then fallback if available
        # Normalize model names (remove 'models/' prefix if present)
        primary_model = self._normalize_model_name(self._model_name)
        models_to_try = [primary_model]
        
        if self._fallback_model_name:
            fallback_model = self._normalize_model_name(self._fallback_model_name)
            if fallback_model != primary_model:
                models_to_try.append(fallback_model)
        
        last_error = None
        for model_name in models_to_try:
            try:
                return self._generate_blog_seo_with_model(title, content, excerpt, model_name)
            except Exception as e:
                error_str = str(e)
                is_overload_error = ("503" in error_str or "overloaded" in error_str.lower() 
                                    or "unavailable" in error_str.lower())
                is_not_found_error = ("404" in error_str or "not found" in error_str.lower())
                
                # 404 errors (model not found) should not trigger fallback, just raise immediately
                if is_not_found_error:
                    raise
                
                # Only try fallback model for overload errors
                if is_overload_error and model_name != models_to_try[-1]:
                    # Try next model if available
                    logger.warning(f"Model {model_name} is overloaded, trying fallback model: {models_to_try[-1]}")
                    last_error = e
                    continue
                else:
                    # Re-raise the error if it's not overloaded or it's the last model
                    raise
        
        # If we get here, all models failed
        if last_error:
            raise last_error
    
    def _generate_blog_seo_with_model(
        self,
        title: str,
        content: str,
        excerpt: Optional[str],
        model_name: str
    ) -> Dict[str, Any]:
        """
        Internal method to generate SEO content with a specific model.
        """
        try:
            # Extract plain text from HTML content if needed
            import re
            if content:
                # Remove HTML tags
                plain_content = re.sub(r'<[^>]+>', '', content)
                # Remove extra whitespace
                plain_content = ' '.join(plain_content.split())
                # Limit content length for prompt
                if len(plain_content) > 2000:
                    plain_content = plain_content[:2000] + "..."
            else:
                plain_content = ""
            
            system_prompt = """You are an SEO expert. Based on the blog post title and content provided, help me create:
1. A SEO-optimized meta title (50-60 characters, in English)
2. A SEO-optimized meta description (120-160 characters, in English)
3. A compelling excerpt/summary (150-200 characters, concise and engaging, in the same language as the content)
4. 3-5 relevant tags (single words or short phrases, in English)

Return the result in JSON format:
{
  "title": "SEO meta title here (50-60 characters)",
  "description": "SEO meta description here (120-160 characters)",
  "excerpt": "Compelling excerpt here (150-200 characters)",
  "tags": ["tag1", "tag2", "tag3"]
}

Important:
- Title should be 50-60 characters, SEO-optimized and engaging
- Description should be 120-160 characters, compelling and include keywords
- Excerpt should be 150-200 characters, concise and engaging, capturing the essence of the article
- Tags should be 3-5 relevant keywords/phrases
- Use English language for title, description, and tags
- Excerpt should match the language of the content if provided
- Focus on SEO best practices"""
            
            content_text = f"Title: {title}\n"
            if excerpt:
                content_text += f"Current Excerpt: {excerpt}\n"
            if plain_content:
                content_text += f"Content: {plain_content}\n"
            
            full_prompt = f"""{system_prompt}

Blog post information:
{content_text}

Please analyze the blog post and generate the SEO title, description, excerpt, and tags. Return only valid JSON."""
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=512
                )
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate and format results
            meta_title = result.get("title", "")[:60]
            meta_description = result.get("description", "")[:160]
            excerpt_text = result.get("excerpt", "")[:200]
            tags = result.get("tags", [])
            
            # Ensure tags is a list and limit to 5
            if not isinstance(tags, list):
                tags = []
            tags = [str(tag).strip() for tag in tags[:5] if tag]
            
            logger.info(f"Successfully generated SEO content using model: {model_name}")
            return {
                "title": meta_title,
                "description": meta_description,
                "excerpt": excerpt_text,
                "tags": tags
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI response. Please try again.")
        except Exception as e:
            error_str = str(e)
            logger.error(f"Failed to generate blog SEO with model {model_name}: {error_str}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Check for specific Gemini API errors and provide friendly messages
            if "404" in error_str or "not found" in error_str.lower():
                raise Exception(f"Gemini model '{model_name}' does not exist or is unavailable. Please verify model name.")
            elif "503" in error_str or "overloaded" in error_str.lower() or "unavailable" in error_str.lower():
                raise Exception("AI overloaded，。")
            elif "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                raise Exception("AI service rate limit exceeded, please try again later.")
            elif "401" in error_str or "403" in error_str or "invalid api key" in error_str.lower():
                raise Exception("Gemini API key is invalid, please check configuration.")
            
            # Re-raise the error so the caller can handle model switching
            raise
    
    def generate_all(
        self,
        prompt_content: str,
        categories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate SEO title, description, tags, and category classification in one call."""
        self._load_config()
        
        try:
            # Format categories for the prompt
            level1_categories = []
            level2_categories = []
            
            for cat in categories:
                if cat.get('level') == 1:
                    level1_categories.append(cat.get('category_name', ''))
                elif cat.get('level') == 2:
                    parent_name = None
                    for parent_cat in categories:
                        if parent_cat.get('id') == cat.get('parent_id'):
                            parent_name = parent_cat.get('category_name')
                            break
                    if parent_name:
                        level2_categories.append(f"{parent_name}|{cat.get('category_name', '')}")
            
            categories_text = "Level 1 Categories:\n"
            for cat in level1_categories:
                categories_text += f"- {cat}\n"
            
            if level2_categories:
                categories_text += "\nLevel 2 Categories:\n"
                for cat in level2_categories:
                    categories_text += f"- {cat}\n"
            
            system_prompt = """You are an SEO expert. Based on the prompt content provided, help me generate:

1. A 60-character SEO title (optimize for moderate search volume, moderate difficulty keywords, in English)
2. A 145-character SEO description (optimize for moderate search volume, moderate difficulty keywords, in English)
3. 0-5 tag words (in English, as a JSON array)
4. The most appropriate category from the provided category list (format: "Level1" or "Level1|Level2", or null if no good match)

Return the result in JSON format:
{
  "title": "SEO title here (exactly 60 characters)",
  "description": "SEO description here (exactly 145 characters)",
  "tags": ["tag1", "tag2", "tag3"],
  "category": "Level1" or "Level1|Level2" or null
}

Important:
- Title must be exactly 60 characters
- Description must be exactly 145 characters
- Tags: 0-5 words maximum, English
- Category: must match one from the provided list, or null
- Use English for all fields
- Focus on keywords with moderate search volume and moderate optimization difficulty"""
            
            full_prompt = f"""{system_prompt}

Prompt content:
{prompt_content}

{categories_text}

Please analyze the prompt content and generate all the required information. Return only valid JSON."""
            
            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )
            
            # Parse JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate and format results
            title = result.get("title", "")[:60]
            description = result.get("description", "")[:145]
            tags = result.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            tags = [str(tag).strip() for tag in tags[:5] if tag]
            
            category = result.get("category")
            # Validate category exists
            if category:
                if "|" in category:
                    if category not in level2_categories:
                        category = None
                else:
                    if category not in level1_categories:
                        category = None
            
            return {
                "title": title,
                "description": description,
                "tags": tags,
                "category": category
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            logger.error(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
            raise Exception("Failed to parse AI response. Please try again.")
        except Exception as e:
            logger.error(f"Failed to generate all content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to generate content: {str(e)}")


    def assist_prompt(
        self,
        prompt_content: str,
        action: str = "optimize",
        model_type: str = "text-to-image"
    ) -> Dict[str, Any]:
        """
        AI prompt assistant to optimize, suggest, or expand prompts.
        
        Args:
            prompt_content: The current prompt text from user
            action: 'optimize', 'suggest', 'expand'
            model_type: The type of generation model (text-to-image, text-to-video, etc.)
            
        Returns:
            Dict containing suggestions and improved text
        """
        self._load_config()
        
        try:
            # Handle "generate" action separately (no user input needed)
            if action == "generate":
                system_prompt = f"""You are a creative AI Prompt Engineer. Generate a complete, professional, and inspiring prompt for {model_type} generation.

The user has no idea what to create, so you need to:
1. Come up with a creative and interesting concept
2. Make it detailed with style, lighting, composition, mood, and technical quality terms
3. Ensure it's optimized for {model_type} models (Stable Diffusion, Midjourney, Flux, Kling, etc.)

Return the response in JSON format:
{{
  "improved_prompt": "A complete, creative, and detailed prompt ready to use",
  "suggestions": ["Alternative creative idea 1", "Alternative creative idea 2", "Alternative creative idea 3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "explanation": "A brief explanation of the creative concept and why it's interesting"
}}

Important:
- Return ONLY valid JSON.
- Be creative and diverse - generate something inspiring and unique
- Make it professional with proper technical terms
- The prompt should be ready to use immediately"""
                
                full_prompt = f"""{system_prompt}

Generate a creative prompt now:"""
            else:
                prompts = {
                    "optimize": f"Rewrite this AI image/video generation prompt to be clearer and more professional. Keep the same core idea but rephrase and improve clarity. Target model: {model_type}.",
                    "expand": f"Expand this prompt by adding relevant keywords, artistic styles, and technical terms used in professional AI prompting. Target model: {model_type}.",
                    "condense": f"Shorten this AI image/video generation prompt while keeping the main subject, style, and key quality terms. Make it concise but still effective. Target model: {model_type}.",
                    "suggest": f"Based on this initial idea, suggest 3 different creative variations for AI generation. Each should have a distinct artistic style. Target model: {model_type}.",
                    "negative": f"Based on this prompt, generate a comprehensive negative prompt (what to avoid) to ensure high quality and avoid common AI artifacts. Target model: {model_type}."
                }
                
                system_instruction = prompts.get(action, prompts["optimize"])
                
                system_prompt = f"""You are an expert AI Prompt Engineer for models like Stable Diffusion, Midjourney, Flux, and Kling.
Your goal is to help users create better prompts for {model_type}.

{system_instruction}

Return the response in JSON format:
{{
  "improved_prompt": "The single best optimized version of the prompt (or negative prompt if that was requested)",
  "suggestions": ["Variation 1", "Variation 2", "Variation 3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "explanation": "Briefly explain what was added and why"
}}

Important:
- Return ONLY valid JSON.
- Use the same language as the input prompt (if user writes in Chinese, explain in Chinese but keep technical keywords in English if appropriate).
- Be creative but stay true to the user's intent."""

                full_prompt = f"""{system_prompt}

User Prompt:
{prompt_content}

Assistant Response:"""

            response = self.client.models.generate_content(
                model=self._model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=1024
                )
            )
            
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            logger.error(f"Failed to assist prompt: {str(e)}")
            raise Exception(f"AI Assistant error: {str(e)}")

    def generate_content_for_workflow(self, prompt: str, params: Dict[str, Any]) -> str:
        """
        Generic text generation for workflow nodes. Used by GeminiProvider.
        Returns raw response text. Supports optional model override and config from params.
        If params contains 'instruction' or 'system_instruction', it is prepended to prompt
        (e.g. for pre-filled "Translate to English" style workflows).
        """
        self._load_config()
        # Optional instruction (pre-filled system prompt); only used by workflow nodes
        instruction = params.pop("instruction", None) or params.pop("system_instruction", None)
        if instruction and isinstance(instruction, str) and instruction.strip():
            prompt = f"{instruction.strip()}\n\n{prompt or ''}"
        model_name = self._normalize_model_name(
            (params.get("model") or params.get("model_name") or "").strip()
        ) or self._model_name
        temperature = float(params.get("temperature", 0.7))
        max_output_tokens = int(params.get("max_output_tokens", params.get("max_tokens", 1024)))
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            ),
        )
        return (response.text or "").strip()


def get_gemini_service(db_session=None) -> GeminiService:
    """
    Get or create GeminiService instance.
    
    Args:
        db_session: Optional database session
        
    Returns:
        GeminiService instance
    """
    # Always create a new instance with the provided db session
    # This ensures we get fresh config from database
    return GeminiService(db_session=db_session)
