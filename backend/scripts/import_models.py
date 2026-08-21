"""Migration script to import existing model configurations into database."""
import sys
import os
from pathlib import Path

# Add backend directory to path so we can import app modules
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal, Base, engine
from app.models.generation_model import GenerationModel, APILibrary

# Original hardcoded configurations
MODELS_DATA = {
    "text2img": {
        "pruna-p-image": {
            "provider": "replicate",
            "task_type": "P-Image",
            "cost": 3, # 🖼️ PrunaAI P-Image
            "provider_model_id": "prunaai/p-image",
            "name": "PrunaAI P-Image",
            "description": "High-quality text-to-image generation with excellent text rendering capabilities",
            "api_docs_url": "https://replicate.com/prunaai/p-image",
            "official_price": 0.005,
            "official_currency": "USD",
            "official_unit": "per output image",
            "notes": "Excellent text rendering performance. Supports custom aspect ratios and prompt upsampling",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe what you want to create. Excellent text rendering capabilities..."},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "16:9", "options": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "custom"]},
                "width": {"type": "int", "name": "Width", "required": False, "default": 1024, "min": 256, "max": 1440, "description": "Custom width. Only effective when aspect_ratio='custom'. Must be a multiple of 16"},
                "height": {"type": "int", "name": "Height", "required": False, "default": 576, "min": 256, "max": 1440, "description": "Custom height. Only effective when aspect_ratio='custom'. Must be a multiple of 16"},
                "prompt_upsampling": {"type": "bool", "name": "Prompt Upsampling", "default": False, "description": "Enable LLM to automatically expand your prompt for richer images"},
                "seed": {"type": "int", "name": "Seed", "default": 0, "min": 0, "max": 2147483647},
                "disable_safety_checker": {"type": "bool", "name": "Disable Safety Checker", "default": False, "description": "Disable built-in image content filter"},
            }
        },
        "flux-schnell": {
            "provider": "replicate",
            "cost": 5, # 🖼️ Fast Image
            "provider_model_id": "black-forest-labs/flux-schnell",
            "name": "FLUX.1 [schnell]",
            "description": "Ultra-fast high-quality text-to-image generation",
            "api_docs_url": "https://replicate.com/black-forest-labs/flux-schnell",
            "official_price": 0.003,
            "official_currency": "USD",
            "official_unit": "per output images",
            "notes": "Fastest high-quality model",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe what you want to create..."},
                "aspect_ratio": {"type": "string", "default": "1:1", "options": ["1:1", "16:9", "21:9", "3:2", "2:3", "4:5", "5:4", "3:4", "4:3", "9:16", "9:21"]},
                "num_inference_steps": {"type": "int", "default": 4, "min": 1, "max": 4},
                "megapixels": {"type": "string", "default": "1", "options": ["1", "0.25"]},
                "go_fast": {"type": "bool", "default": True},
                "output_quality": {"type": "int", "default": 80, "min": 0, "max": 100},
                "seed": {"type": "int", "default": 0, "min": 0, "max": 9999999999},
                "disable_safety_checker": {"type": "bool", "default": False},
            }
        },
        "imagen-4-fast": {
            "provider": "replicate",
            "cost": 10, # 🖼️ Google Imagen-4-Fast (Newest and cheaper)
            "provider_model_id": "google/imagen-4-fast",
            "name": "Google Imagen-4-Fast",
            "description": "Google's latest ultra-fast high-quality text-to-image model",
            "api_docs_url": "https://replicate.com/google/imagen-4-fast",
            "official_price": 0.02,
            "official_currency": "USD",
            "official_unit": "per output image",
            "notes": "Excellent quality with much lower latency and cost",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe what you want to create..."},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "1:1", "options": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]},
                "safety_filter_level": {"type": "string", "name": "Safety Filter", "default": "block_only_high", "options": ["block_low_and_above", "block_medium_and_above", "block_only_high"]},
            }
        },
        "a2e-flux-1-schnell": {
            "provider": "a2e",
            "cost": 3,
            "model_level": "member",
            "provider_model_id": "flux-1-schnell",
            "name": "A2E Flux.1 Schnell",
            "description": "Fast high-quality text-to-image generation via A2E",
            "api_docs_url": "https://video.a2e.ai/",
            "official_price": 0.01,
            "official_currency": "USD",
            "official_unit": "per image",
            "notes": "Cost-effective flux generation",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe what you want to create..."},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "1:1", "options": ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]},
                "resolution": {"type": "string", "name": "Resolution", "default": "1080p", "options": ["1080p", "2k", "4k"]},
            }
        },
    },
    "img2img": {
        "flux-redux": {
            "provider": "replicate",
            "cost": 5, # 🖼️ Image variants
            "provider_model_id": "black-forest-labs/flux-redux-schnell",
            "name": "FLUX.1 Redux [schnell]",
            "description": "Generate high-quality image variations based on a reference image",
            "api_docs_url": "https://replicate.com/black-forest-labs/flux-redux-schnell",
            "official_price": 0.003,
            "official_currency": "USD",
            "official_unit": "per output images",
            "notes": "Style and content variations",
            "params": {
                "redux_image": {"type": "image", "name": "Reference Image", "required": True},
                "aspect_ratio": {"type": "string", "default": "1:1", "options": ["1:1", "16:9", "21:9", "3:2", "2:3", "4:5", "5:4", "3:4", "4:3", "9:16", "9:21"]},
                "megapixels": {"type": "string", "default": "1", "options": ["1", "0.25"]},
                "num_inference_steps": {"type": "int", "default": 4, "min": 1, "max": 4},
                "output_quality": {"type": "int", "default": 80, "min": 0, "max": 100},
                "seed": {"type": "int", "default": 0, "min": 0, "max": 9999999999},
                "disable_safety_checker": {"type": "bool", "default": False},
            }
        },
        "nano-banana-pro": {
            "provider": "replicate",
            "cost": 25, # 🖼️ Google Nano-Banana-Pro
            "provider_model_id": "google/nano-banana-pro",
            "name": "Google Nano-Banana-Pro",
            "description": "Powerful image-to-image and reference-based generation with support for multiple input images",
            "api_docs_url": "https://replicate.com/google/nano-banana-pro",
            "official_price": 0.15,
            "official_currency": "USD",
            "official_unit": "per output image",
            "notes": "Excellent for image variations and reference-based generation. Supports up to 14 input images.",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe what you want to create (supports multi-line)..."},
                "image_input": {"type": "image", "name": "Input Images", "required": False, "multiple": True, "description": "Used for transformations or as a reference. Up to 14 images supported"},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "match_input_image", "options": ["match_input_image", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]},
                "resolution": {"type": "string", "name": "Resolution", "default": "2K", "options": ["1K", "2K"
                # , "4K"
                ]},
                "safety_filter_level": {"type": "string", "name": "Safety Filter", "default": "block_only_high", "options": ["block_low_and_above", "block_medium_and_above", "block_only_high"]},
            }
        },
    },
    "text2video": {
        "luma-ray-flash-v2": {
            "provider": "replicate",
            "cost": 30, # ⚡ Faster and cheaper
            "provider_model_id": "luma/ray-flash-2-720p",
            "name": "Luma Ray Flash 2.0 (T2V)",
            "description": "Fast 720p video generation with Flash 2.0",
            "api_docs_url": "https://replicate.com/luma/ray-flash-2-720p",
            "official_price": 0.06,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "Faster version of Ray, good for quick previews",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "min_length": 3, "multiline": True, "placeholder": "Describe what you want to see..."},
                "duration": {"type": "int", "default": 5, "options": [5, 9]},
                "aspect_ratio": {"type": "string", "default": "16:9", "options": ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]},
                "loop": {"type": "bool", "name": "Loop", "default": False},
                "concepts": {"type": "text", "name": "Camera Language", "default": "", "placeholder": "e.g. zoom_in, pan_left, handheld..."},
            }
        },
        "veo-3-fast": {
            "provider": "replicate",
            "cost": 65, # 🎬 Google Veo 3 Fast (T2V)
            "provider_model_id": "google/veo-3-fast",
            "name": "Google Veo 3 Fast (T2V)",
            "description": "High-quality text-to-video generation with excellent camera control understanding",
            "api_docs_url": "https://replicate.com/google/veo-3-fast",
            "official_price": 0.15,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "Excellent understanding of camera instructions (pan, rotate, etc.) and native audio generation",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "min_length": 3, "multiline": True, "placeholder": "Describe the scene and motion (e.g., 'Rotate the shoe'). Veo understands camera instructions well..."},
                "generate_audio": {"type": "bool", "name": "Generate Audio", "default": True, "description": "Generate native audio that matches the environment"},
                "duration": {"type": "int", "name": "Duration", "default": 8, "options": [4, 6, 8]},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "16:9", "options": ["16:9", "9:16"]},
                "resolution": {"type": "string", "name": "Resolution", "default": "720p", 
                "options": ["720p"
                # ,"1080p"
                ]},
                "negative_prompt": {"type": "text", "name": "Negative Prompt", "required": False, "multiline": True, "placeholder": "Describe what you don't want in the video..."},
                "seed": {"type": "int", "name": "Seed", "default": 0, "min": 0, "max": 2147483647},
            }
        },
    },
    "img2video": {
        "wan-2.2-i2v-fast": {
            "provider": "replicate",
            "cost": 25, # 🎬 WAN 2.2 I2V Fast
            "provider_model_id": "wan-video/wan-2.2-i2v-fast",
            "name": "WAN 2.2 I2V Fast",
            "description": "Fast image-to-video generation with advanced motion control and LoRA support",
            "api_docs_url": "https://replicate.com/wan-video/wan-2.2-i2v-fast",
            "official_price": 0.145,
            "official_currency": "USD",
            "official_unit": "per output video",
            "notes": "Supports frame interpolation, LoRA weights, and advanced sampling controls",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the motion, lighting changes, and camera movement..."},
                "image": {"type": "image", "name": "First Frame", "required": True},
                "last_image": {"type": "image", "name": "Last Frame", "required": False, "placeholder": "If provided, creates transition animation from first to last frame"},
                "resolution": {"type": "string", "name": "Resolution", "default": "480p", "options": ["480p", "720p"]},
                "num_frames": {"type": "int", "name": "Number of Frames", "default": 81, "min": 81, "max": 121},
                "frames_per_second": {"type": "int", "name": "FPS", "default": 16, "min": 5, "max": 30},
                "interpolate_output": {"type": "bool", "name": "Interpolate Output", "default": False, "description": "Use ffmpeg to interpolate frames to 30 FPS for smoother video"},
                "go_fast": {"type": "bool", "name": "Fast Mode", "default": True},
                "sample_shift": {"type": "float", "name": "Sample Shift", "default": 12, "min": 1, "max": 20, "description": "Adjust distribution shift during generation"},
                "seed": {"type": "int", "name": "Seed", "default": 0, "min": 0, "max": 2147483647},
                "disable_safety_checker": {"type": "bool", "name": "Disable Safety Checker", "default": False},
                "lora_weights_transformer": {"type": "text", "name": "LoRA Weights URL", "required": False, "placeholder": "URL to external .safetensors style model for Transformer"},
                "lora_scale_transformer": {"type": "float", "name": "LoRA Scale", "default": 1, "min": 0, "max": 2, "description": "Adjust LoRA influence weight"},
            }
        },
        "seedance-1-pro-fast-i2v": {
            "provider": "replicate",
            "cost": 25, # 🎬 ByteDance SeeDance 1 Pro Fast (I2V)
            "provider_model_id": "bytedance/seedance-1-pro-fast",
            "name": "SeeDance 1 Pro Fast (I2V)",
            "description": "High-quality image-to-video generation with excellent cinematic style support",
            "api_docs_url": "https://replicate.com/bytedance/seedance-1-pro-fast",
            "official_price": 0.06,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "Upload image to enable I2V mode. If image is provided, aspect_ratio will be ignored. Excellent cinematic support and flexible duration (2-12s)",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the video content. Excellent support for cinematic descriptions (e.g., supercar, sunset, cinematic lighting)..."},
                "image": {"type": "image", "name": "Start Image", "required": True, "description": "First frame of the video. Upload to enable I2V mode. If provided, aspect_ratio will be ignored"},
                "resolution": {"type": "string", "name": "Resolution", "default": "1080p", "options": ["480p", "720p", "1080p"], "description": "Different resolutions have tiered pricing"},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "16:9", "options": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "9:21"], "description": "Wide aspect ratio support. Ignored if image is provided"},
                "duration": {"type": "int", "name": "Duration", "default": 5, "min": 2, "max": 12, "description": "Flexible duration range from 2 to 12 seconds"},
                "camera_fixed": {"type": "bool", "name": "Camera Fixed", "default": False, "description": "If true, locks camera position (only objects move). If false, allows camera pan/tilt/zoom"},
                "fps": {"type": "int", "name": "FPS", "default": 24, "description": "Fixed at 24 FPS, standard cinematic frame rate"},
                "seed": {"type": "int", "name": "Seed", "default": 0, "min": 0, "max": 2147483647, "description": "Random seed for fixing generation results, useful for debugging the same shot"},
            }
        },
        "luma-ray-flash-v2-i2v": {
            "provider": "replicate",
            "cost": 30,
            "provider_model_id": "luma/ray-flash-2-720p",
            "name": "Luma Ray Flash 2.0 (I2V)",
            "description": "Fast 720p image-to-video generation",
            "api_docs_url": "https://replicate.com/luma/ray-flash-2-720p",
            "official_price": 0.06,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "Faster and cheaper Flash version",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the motion..."},
                "start_image": {"type": "image", "name": "Start Frame", "required": False},
                "end_image": {"type": "image", "name": "End Frame", "required": False},
                "duration": {"type": "int", "default": 5, "options": [5, 9]},
                "aspect_ratio": {"type": "string", "default": "16:9", "options": ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]},
                "loop": {"type": "bool", "name": "Loop", "default": False},
                "concepts": {"type": "text", "name": "Camera Language", "default": "", "placeholder": "e.g. zoom_in, pan_left, handheld..."},
            }
        },
        "kling-v2.1": {
            "provider": "replicate",
            "cost": 40, # 🎬 Kling v2.1 (I2V)
            "provider_model_id": "kwaivgi/kling-v2.1",
            "name": "Kling v2.1",
            "description": "Advanced image-to-video generation with Pro mode support for 1080p quality and end frame control",
            "api_docs_url": "https://replicate.com/kwaivgi/kling-v2.1",
            "official_price": 0.09,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "v2.1 requires start_image (text-only generation not supported). Pro mode supports end_image for coherent motion between frames",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the motion in the scene (e.g., 'woman takes her hands out her pockets')..."},
                "start_image": {"type": "image", "name": "Start Image", "required": True, "description": "First frame of the video. Required in v2.1, text-only generation not supported"},
                "mode": {"type": "string", "name": "Mode", "default": "standard", "options": ["standard", "pro"], "description": "standard: 720p resolution, pro: 1080p resolution with higher quality"},
                "duration": {"type": "int", "name": "Duration", "default": 5, "options": [5, 10]},
                "end_image": {"type": "image", "name": "End Image", "required": False, "description": "Last frame of the video. Only supported in Pro mode. Model will generate coherent motion between start and end frames"},
                "negative_prompt": {"type": "text", "name": "Negative Prompt", "default": "", "required": False, "multiline": True, "placeholder": "Exclude unwanted elements (e.g., deformed limbs, blur)"},
            }
        },
        "veo-3-fast-i2v": {
            "provider": "replicate",
            "cost": 65, # 🎬 Google Veo 3 Fast (I2V)
            "provider_model_id": "google/veo-3-fast",
            "name": "Google Veo 3 Fast (I2V)",
            "description": "High-quality image-to-video generation with excellent camera control understanding",
            "api_docs_url": "https://replicate.com/google/veo-3-fast",
            "official_price": 0.15,
            "official_currency": "USD",
            "official_unit": "per second of output video",
            "notes": "Upload image as first frame. Excellent understanding of camera instructions and native audio generation",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the scene and motion (e.g., 'Rotate the shoe'). Veo understands camera instructions well..."},
                "image": {"type": "image", "name": "Start Image", "required": True, "description": "First frame of the video. Recommended resolution matches aspect_ratio (1280x720 or 720x1280)"},
                "generate_audio": {"type": "bool", "name": "Generate Audio", "default": True, "description": "Generate native audio that matches the environment"},
                "duration": {"type": "int", "name": "Duration", "default": 8, "options": [4, 6, 8]},
                "aspect_ratio": {"type": "string", "name": "Aspect Ratio", "default": "16:9", "options": ["16:9", "9:16"]},
                "resolution": {"type": "string", "name": "Resolution", "default": "720p", "options": ["720p"
                # ,"1080p"
                ]},
                "negative_prompt": {"type": "text", "name": "Negative Prompt", "required": False, "multiline": True, "placeholder": "Describe what you don't want in the video..."},
                "seed": {"type": "int", "name": "Seed", "default": 0, "min": 0, "max": 2147483647},
            }
        },
        "a2e-wan2.6-i2v": {
            "provider": "a2e",
            "cost": 15,
            "model_level": "premium",
            "provider_model_id": "wan2.6-i2v-flash",
            "name": "A2E Wan 2.6 I2V",
            "description": "High-quality image-to-video generation powered by Wan 2.6",
            "api_docs_url": "https://video.a2e.ai/",
            "official_price": 0.05,
            "official_currency": "USD",
            "official_unit": "per video",
            "notes": "Excellent motion and quality. Optimized for 720p 5s-15s clips.",
            "params": {
                "prompt": {"type": "text", "name": "Prompt", "required": True, "multiline": True, "placeholder": "Describe the motion..."},
                "image_url": {"type": "image", "name": "Start Image", "required": True},
                "duration": {"type": "string", "name": "Duration", "default": "5", "options": ["5", "10", "15"]},
                "resolution": {"type": "string", "name": "Resolution", "default": "720p", "options": ["480p", "720p", "1080p"]},
                "audio": {"type": "bool", "name": "Enable Audio", "default": True},
                "enable_prompt_expansion": {"type": "bool", "name": "Prompt Expansion", "default": False},
                "seed": {"type": "int", "name": "Seed", "required": False},
            }
        },
    }
}

def main():
    """Import all models from hardcoded data into database."""
    db = SessionLocal()
    try:
        imported_count = 0
        updated_count = 0
        api_count = 0
        
        for work_type, models_dict in MODELS_DATA.items():
            for model_key, config in models_dict.items():
                # Extract provider info
                provider = config.get("provider")
                provider_model_id = config.get("provider_model_id") or config.get("model_id") or config.get("replicate_model")
                
                if not provider_model_id:
                    print(f"⚠️ Warning: Missing provider_model_id for {model_key}, skipping.")
                    continue

                # 1. Handle API Library entry
                # We use provider_model_id as a heuristic for finding/creating API entries
                api_key_suggestion = f"{provider}_{provider_model_id.replace('/', '_').replace('.', '_')}"
                api_entry = db.query(APILibrary).filter(
                    APILibrary.provider == provider,
                    APILibrary.provider_model_id == provider_model_id
                ).first()

                if api_entry:
                    # Update task_type if provided and missing
                    if not api_entry.task_type and config.get("task_type"):
                        api_entry.task_type = config.get("task_type")
                else:
                    # Create new API entry
                    api_entry = APILibrary(
                        api_key=api_key_suggestion,
                        name=config.get("name", model_key),
                        task_type=config.get("task_type") or work_type.replace('2', ' to '),
                        provider=provider,
                        provider_model_id=provider_model_id,
                        params_schema=config.get("params", {}),
                        api_docs_url=config.get("api_docs_url"),
                        official_price=config.get("official_price"),
                        official_currency=config.get("official_currency", "USD"),
                        official_unit=config.get("official_unit"),
                        notes=f"Auto-imported for {model_key}"
                    )
                    db.add(api_entry)
                    db.flush() # Get ID
                    api_count += 1
                    print(f"Created API Entry: {api_key_suggestion}")
                
                # 2. Handle Generation Model entry
                existing = db.query(GenerationModel).filter(
                    GenerationModel.model_key == model_key
                ).first()

                model_fields = {
                    "name": config.get("name", model_key),
                    "work_type": work_type,
                    "description": config.get("description"),
                    "cost": config.get("cost", 0),
                    "params_config": {}, # Initially empty overrides
                    "model_level": config.get("model_level", "public"),
                    "category": "general",
                    "notes": config.get("notes"),
                    "is_active": True
                }
                
                if existing:
                    # Update existing model
                    for key, value in model_fields.items():
                        setattr(existing, key, value)
                    updated_count += 1
                    print(f"Updated Model: {work_type}/{model_key}")
                else:
                    # Create new model
                    new_model = GenerationModel(
                        model_key=model_key,
                        sort_order=0,
                        **model_fields
                    )
                    db.add(new_model)
                    imported_count += 1
                    print(f"Imported Model: {work_type}/{model_key}")
        
        db.commit()
        print(f"\n✅ Import completed!")
        print(f"   - API Entries: {api_count} created")
        print(f"   - Models Imported: {imported_count}")
        print(f"   - Models Updated: {updated_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during import: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
