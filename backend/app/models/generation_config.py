"""Configuration for AI generation models.

This module reads models from the database and caches them for performance.
Primary cache: Redis (shared across workers/instances).
Fallback: in-process cache (only used if Redis is unavailable).
"""

from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

# Cache for models loaded from database
_models_cache: Optional[Dict] = None
_cache_timestamp: Optional[float] = None
CACHE_TTL = 300  # Cache for 5 minutes

# Redis cache key (without global prefix; prefix applied in redis_cache.build_key)
_REDIS_MODELS_KEY = "models:active:v2"

WORK_TYPE_ALIASES = {
    "text2img": "text-to-image",
    "img2img": "image-to-image",
    "text2video": "text-to-video",
    "img2video": "image-to-video",
    "img_effects": "image-effects",
    "vid_effects": "video-effects",
}


def normalize_work_type(work_type: str) -> str:
    """Return the canonical work type while preserving unknown extensions."""
    normalized = (work_type or "").strip().lower()
    return WORK_TYPE_ALIASES.get(normalized, normalized)


def _load_models_from_db(force_refresh: bool = False) -> Dict:
    """
    Load models from database with caching.
    
    Args:
        force_refresh: Force reload from database, ignoring cache
        
    Returns:
        Dictionary of models by work_type
    """
    global _models_cache, _cache_timestamp
    
    # 1) Check Redis cache first (unless force refresh)
    if not force_refresh:
        try:
            from ..utils.redis_cache import get_json

            cached = get_json(_REDIS_MODELS_KEY)
            if isinstance(cached, dict):
                return cached
        except Exception:
            # Degrade gracefully to in-process cache / DB
            pass

    # 2) Fallback to in-process cache (unless force refresh)
    if not force_refresh and _models_cache is not None:
        if _cache_timestamp is not None and time.time() - _cache_timestamp < CACHE_TTL:
            return _models_cache
    
    try:
        from .base import SessionLocal
        from .generation_model import GenerationModel, APILibrary
        from sqlalchemy.orm import joinedload

        db = SessionLocal()
        try:
            db_models = db.query(GenerationModel).options(
                joinedload(GenerationModel.workflow)
            ).filter(
                GenerationModel.is_active == True
            ).order_by(
                GenerationModel.work_type,
                GenerationModel.sort_order,
                GenerationModel.id
            ).all()

            models_dict: Dict = {}
            for model in db_models:
                try:
                    work_type = normalize_work_type(model.work_type) or "unknown"
                    if work_type not in models_dict:
                        models_dict[work_type] = {}

                    config = model.to_dict()
                    # Enrich with primary API from first api_call node of workflow
                    if model.workflow and model.workflow.nodes:
                        for node in model.workflow.nodes:
                            if node.get("type") == "api_call" and node.get("api_id"):
                                api = db.query(APILibrary).filter(APILibrary.id == node["api_id"]).first()
                                if api:
                                    config["api_id"] = api.id
                                    config["api_name"] = api.name
                                    config["provider"] = api.provider
                                    config["provider_model_id"] = api.provider_model_id
                                    config["api_docs_url"] = api.api_docs_url
                                    config["official_price"] = api.official_price
                                    config["official_currency"] = api.official_currency
                                    config["official_unit"] = api.official_unit
                                    config["model_id"] = api.provider_model_id
                                break
                    models_dict[work_type][model.model_key] = config
                except Exception as e:
                    logger.error(f"Error converting model {model.id} ({model.model_key}) to dict: {str(e)}")
                    continue
            
            # Update cache
            _models_cache = models_dict
            _cache_timestamp = time.time()

            # Update Redis cache (best-effort)
            try:
                from ..utils.redis_cache import set_json

                set_json(_REDIS_MODELS_KEY, models_dict, CACHE_TTL)
            except Exception:
                pass
            
            logger.info(f"Loaded {len(db_models)} models from database")
            return models_dict
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to load models from database: {str(e)}")
        # Return empty dict if DB is inaccessible
        return {}


def get_models() -> Dict:
    """
    Get all active models from database.
    """
    return _load_models_from_db()


# Proxy class to maintain backward compatibility with 'MODELS' dictionary access
class _ModelsProxy:
    """Proxy class to maintain backward compatibility with MODELS dict."""
    
    def __getitem__(self, key):
        return get_models()[key]
    
    def __contains__(self, key):
        return key in get_models()
    
    def keys(self):
        return get_models().keys()
    
    def items(self):
        return get_models().items()
    
    def values(self):
        return get_models().values()
    
    def get(self, key, default=None):
        return get_models().get(key, default)

MODELS = _ModelsProxy()


def invalidate_cache():
    """Invalidate the models cache."""
    global _models_cache, _cache_timestamp
    _models_cache = None
    _cache_timestamp = None
    logger.info("Models cache invalidated")

    # Invalidate Redis cache (best-effort)
    try:
        from ..utils.redis_cache import delete

        delete(_REDIS_MODELS_KEY)
    except Exception:
        pass


def get_model_config(work_type: str, model_name: str) -> dict:
    """
    Get configuration for a specific model from database.
    """
    models = get_models()
    work_type = normalize_work_type(work_type)
    
    if work_type not in models:
        raise ValueError(f"Invalid work type or no active models: {work_type}")
    
    if model_name not in models[work_type]:
        raise ValueError(f"Model '{model_name}' not found for type '{work_type}'")
    
    return models[work_type][model_name]


def get_available_models(work_type: str) -> dict:
    """
    Get all available active models for a work type.
    """
    return get_models().get(normalize_work_type(work_type), {})


def get_model_cost(work_type: str, model_name: str, params: dict = None) -> int:
    """
    Get the credit cost for a model, optionally with dynamic cost based on parameters.
    
    Args:
        work_type: Type of work (text-to-image, image-to-video, etc.)
        model_name: Model key/name
        params: Optional parameters dict to calculate dynamic cost additions.
                If provided, will calculate base cost + parameter-based additions.
                If None, returns only base cost.
        
    Returns:
        Total cost (base cost + parameter-based additions)
        
    Example:
        # Base cost only
        cost = get_model_cost("text-to-video", "veo-3-fast")
        
        # With dynamic cost based on parameters
        params = {"duration": 8, "resolution": "720p"}
        cost = get_model_cost("text-to-video", "veo-3-fast", params)
    """
    config = get_model_config(work_type, model_name)
    base_cost = config["cost"]
    
    # If no params provided, return base cost (backward compatible)
    if params is None:
        return base_cost
    
    # Calculate additional costs from parameters
    param_definitions = config.get("params", {})
    additional_cost = 0
    
    for param_key, param_value in params.items():
        # Skip if parameter not defined in config
        if param_key not in param_definitions:
            continue
            
        param_def = param_definitions[param_key]
        cost_additions = param_def.get("cost_additions")
        
        # Skip if no cost_additions defined for this parameter
        if cost_additions is None:
            continue
        
        # Handle dict-based cost_additions: {"5": 0, "8": 10}  "_ranges": [[min, max, cost], ...]
        if isinstance(cost_additions, dict):
            # Normalize so bool True/False matches config keys "true"/"false" (from JSON/admin)
            param_value_str = str(param_value).lower() if isinstance(param_value, bool) else str(param_value)
            cost_addition = None

            # 1) ：param_value  key
            if param_value_str in cost_additions:
                cost_addition = cost_additions[param_value_str]

            # 2) ：_ranges = [[min, max, cost], ...]， cost
            if cost_addition is None and "_ranges" in cost_additions:
                ranges = cost_additions["_ranges"]
                if isinstance(ranges, list):
                    try:
                        num_value = float(param_value) if isinstance(param_value, (int, float)) else float(param_value)
                    except (TypeError, ValueError):
                        num_value = None
                    if num_value is not None:
                        for r in ranges:
                            if isinstance(r, (list, tuple)) and len(r) >= 3:
                                r_min, r_max = float(r[0]), float(r[1])
                                r_cost = r[2]
                                if r_min <= num_value <= r_max:
                                    cost_addition = r_cost
                                    break

            if cost_addition is not None:
                if isinstance(cost_addition, (int, float)):
                    additional_cost += int(cost_addition)
                else:
                    logger.warning(
                        f"Invalid cost_additions value for {param_key}={param_value}: "
                        f"expected number, got {type(cost_addition)}"
                    )
    
    total_cost = base_cost + additional_cost
    logger.debug(
        f"Cost calculation for {work_type}/{model_name}: "
        f"base={base_cost}, additions={additional_cost}, total={total_cost}"
    )
    
    return total_cost


def validate_params(work_type: str, model_name: str, params: dict) -> tuple[bool, dict]:
    """
    Validate and sanitize generation parameters against database definitions.
    """
    try:
        config = get_model_config(work_type, model_name)
        param_definitions = config.get("params", {})
        
        sanitized = {}
        errors = {}
        
        for key, definition in param_definitions.items():
            value = params.get(key)
            
            # Use default if not provided
            if value is None:
                if definition.get("required"):
                    errors[key] = "This parameter is required"
                else:
                    # Only add default if it exists in definition and is not None
                    # This prevents sending 'null' to providers that are strict about types
                    if "default" in definition and definition["default"] is not None:
                        sanitized[key] = definition["default"]
                continue
            
            # Validate based on type
            param_type = definition.get("type")
            
            if param_type == "int":
                try:
                    value = int(value)
                    if "min" in definition and value < definition["min"]:
                        errors[key] = f"Value must be >= {definition['min']}"
                    elif "max" in definition and value > definition["max"]:
                        errors[key] = f"Value must be <= {definition['max']}"
                    elif "options" in definition and value not in definition["options"]:
                        errors[key] = f"Value must be one of {definition['options']}"
                    else:
                        sanitized[key] = value
                except ValueError:
                    errors[key] = "Invalid integer value"
            
            elif param_type == "float":
                try:
                    value = float(value)
                    if "min" in definition and value < definition["min"]:
                        errors[key] = f"Value must be >= {definition['min']}"
                    elif "max" in definition and value > definition["max"]:
                        errors[key] = f"Value must be <= {definition['max']}"
                    else:
                        sanitized[key] = value
                except ValueError:
                    errors[key] = "Invalid float value"
            
            elif param_type == "image":
                if isinstance(value, list):
                    # Handle multiple images
                    valid_images = []
                    for img in value:
                        if isinstance(img, str) and (img.startswith("http") or img.startswith("data:image")):
                            valid_images.append(img)
                        else:
                            errors[key] = f"Invalid image URL or base64 data in list"
                            break
                    if key not in errors:
                        sanitized[key] = valid_images
                elif value and not (isinstance(value, str) and (value.startswith("http") or value.startswith("data:image"))):
                    errors[key] = "Invalid image URL or base64 data"
                else:
                    sanitized[key] = value
            
            elif param_type == "bool":
                sanitized[key] = bool(value)
            
            elif param_type == "text":
                if not isinstance(value, str):
                    errors[key] = "Value must be a string"
                elif definition.get("required") and not value.strip():
                    errors[key] = "This parameter is required"
                elif "min_length" in definition and len(value.strip()) < definition["min_length"]:
                    errors[key] = f"Value must be at least {definition['min_length']} characters long"
                elif "max_length" in definition and len(value.strip()) > definition["max_length"]:
                    errors[key] = f"Value must be at most {definition['max_length']} characters long"
                else:
                    sanitized[key] = value
            
            else:
                sanitized[key] = value
        
        if errors:
            return False, errors
        
        return True, sanitized
        
    except ValueError as e:
        return False, {"error": str(e)}
