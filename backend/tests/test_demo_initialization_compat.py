import json
from pathlib import Path

from app.models.generation_config import normalize_work_type
from app.services import storage as storage_module
from app.utils.seed_sanitizer import contains_production_domain, sanitize_seed_data


def test_legacy_work_types_are_normalized():
    assert normalize_work_type("text2img") == "text-to-image"
    assert normalize_work_type("img2img") == "image-to-image"
    assert normalize_work_type("text2video") == "text-to-video"
    assert normalize_work_type("img2video") == "image-to-video"
    assert normalize_work_type("video-effects") == "video-effects"


def test_local_storage_can_serialize_external_cdn_urls(monkeypatch):
    monkeypatch.setattr(storage_module, "R2_ENDPOINT", None)
    monkeypatch.setattr(storage_module, "R2_ACCESS_KEY", None)
    monkeypatch.setattr(storage_module, "R2_SECRET_KEY", None)
    monkeypatch.setattr(storage_module, "R2_BUCKET_NAME", None)
    service = storage_module.StorageService()

    cdn_url = "https://cdn.vidgenerator.ai/demo.webp"
    assert service.is_local is True
    assert service.get_public_url(cdn_url) == cdn_url


def test_seed_sanitizer_replaces_domains_in_nested_content():
    source = {
        "url": "https://vidgenerator.ai/generate",
        "nested": ["https://cdn.vidgenerator.ai/image.webp", "VidGenerator.ai"],
    }

    sanitized = sanitize_seed_data(source)

    assert sanitized["url"] == "https://example.com/generate"
    assert sanitized["nested"] == [
        "https://cdn.vidgenerator.ai/image.webp",
        "example.com",
    ]
    assert not contains_production_domain(sanitized)


def test_seed_sanitizer_redacts_and_disables_tracking_code():
    source = {
        "config_key": "custom_code_head_demo",
        "is_enabled": True,
        "config_value": (
            '<meta name="google-site-verification" content="real-looking-token" />'
            '<script src="https://www.googletagmanager.com/gtag/js?id=G-ABC123XYZ9"></script>'
            "<script>gtag('config', 'AW-12345678901');</script>"
            '(window, document, "clarity", "script", "project123");'
        ),
    }

    sanitized = sanitize_seed_data(source)

    assert sanitized["is_enabled"] is False
    assert "real-looking-token" not in sanitized["config_value"]
    assert "G-ABC123XYZ9" not in sanitized["config_value"]
    assert "AW-12345678901" not in sanitized["config_value"]
    assert "project123" not in sanitized["config_value"]
    assert "YOUR_GOOGLE_SITE_VERIFICATION_TOKEN" in sanitized["config_value"]
    assert "G-XXXXXXXXXX" in sanitized["config_value"]
    assert "AW-00000000000" in sanitized["config_value"]
    assert "YOUR_CLARITY_PROJECT_ID" in sanitized["config_value"]


def test_tracking_sanitizer_does_not_modify_normal_content():
    source = {
        "content": "image-generator and slug-generator remain intact",
        "model_key": "legacy-import-g-example",
        "url": "https://example.com/blog/long-form-guide",
    }

    assert sanitize_seed_data(source) == source


def test_checked_in_seed_dataset_contains_no_production_domain():
    seed_dir = Path(__file__).resolve().parents[1] / "scripts" / "seed_data"
    offending_files = []

    for seed_file in sorted(seed_dir.glob("*.json")):
        with seed_file.open(encoding="utf-8") as file_handle:
            if contains_production_domain(json.load(file_handle)):
                offending_files.append(seed_file.name)

    assert offending_files == []


def test_checked_in_tracking_configs_are_disabled_and_redacted():
    seed_file = (
        Path(__file__).resolve().parents[1] / "scripts" / "seed_data" / "seo_configs.json"
    )
    with seed_file.open(encoding="utf-8") as file_handle:
        custom_codes = [
            item
            for item in json.load(file_handle)
            if str(item.get("config_key", "")).startswith("custom_code_")
        ]

    assert custom_codes
    assert all(item["is_enabled"] is False for item in custom_codes)
    serialized = json.dumps(custom_codes)
    assert "v1rhg2mvpf" not in serialized
    assert "q4MgbZI2aKZdsZeOVPOGBJ9HHSvTt7VE_Ulv5e6oV08" not in serialized
    assert "G-WR2PSF0X8G" not in serialized
    assert "AW-18021646634" not in serialized
