import json
from collections import Counter
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
        "nested": [
            "https://cdn.vidgenerator.ai/image.webp",
            "VidGenerator.ai",
            "https://example.com/topic/demo",
            "admin@example.com",
        ],
    }

    sanitized = sanitize_seed_data(source)

    assert sanitized["url"] == "http://localhost:3000/generate"
    assert sanitized["nested"] == [
        "https://cdn.vidgenerator.ai/image.webp",
        "localhost:3000",
        "http://localhost:3000/topic/demo",
        "admin@example.com",
    ]
    assert not contains_production_domain(sanitized)


def test_seed_sanitizer_preserves_external_media():
    source = {"thumbnail_url": "https://media.example.test/demo.webp"}
    assert sanitize_seed_data(source)["thumbnail_url"] == source["thumbnail_url"]


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
        "url": "http://localhost:3000/blog/long-form-guide",
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


def test_demo_works_fill_every_explore_category_and_users_are_anonymized():
    seed_dir = Path(__file__).resolve().parents[1] / "scripts" / "seed_data"
    with (seed_dir / "sample_works.json").open(encoding="utf-8") as file_handle:
        works = json.load(file_handle)
    with (seed_dir / "sample_users.json").open(encoding="utf-8") as file_handle:
        users = json.load(file_handle)
    with (seed_dir / "generation_models.json").open(encoding="utf-8") as file_handle:
        models = json.load(file_handle)

    assert all(work["file_url"].startswith("https://") for work in works)
    assert all(work["thumbnail_url"].startswith("https://") for work in works)
    assert all(work["is_shared"] is True for work in works)
    assert all(work["share_status"].lower() == "approved" for work in works)
    assert all(work.get("nsfw_status") in (None, "APPROVED", "approved") for work in works)
    preview_videos = [
        work for work in works
        if work["type"] in {"text-to-video", "image-to-video"} and work["is_featured"]
    ]
    assert len(preview_videos) >= 30
    assert Counter(work["type"] for work in preview_videos) == {
        "text-to-video": 15,
        "image-to-video": 15,
    }
    assert sum(
        (work.get("params") or {}).get("aspect_ratio") in {"16:9", "landscape"}
        for work in preview_videos
    ) >= 30

    user_ids = {user["id"] for user in users}
    assert {work["user_id"] for work in works}.issubset(user_ids)
    assert all(user["email"].endswith("@example.invalid") for user in users)
    assert all(user["handle"].startswith("demo_user_") for user in users)
    assert all(len(user["handle"]) <= 15 for user in users)
    assert all(user["nickname"].startswith("Demo Creator ") for user in users)
    assert all(user["avatar_url"] is None for user in users)

    models_by_key = {model["model_key"]: model for model in models}
    assert all(work["model_key"] in models_by_key for work in works)
    assert all(
        work["model_name"] == models_by_key[work["model_key"]]["name"]
        and work["type"] == models_by_key[work["model_key"]]["work_type"]
        for work in works
    )

    with (seed_dir / "category_pages.json").open(encoding="utf-8") as file_handle:
        categories = json.load(file_handle)
    explore_categories = {
        item["category_name"]
        for item in categories
        if item.get("is_active") and item.get("show_in_explore") and item.get("level") == 1
    }
    category_counts = Counter(
        str(work.get("category") or "").split("|", 1)[0]
        for work in works
    )
    assert set(category_counts) == explore_categories
    assert set(category_counts.values()) == {10}
    assert len(works) == len(explore_categories) * 10


def test_seed_model_bundle_has_no_unreferenced_history():
    seed_dir = Path(__file__).resolve().parents[1] / "scripts" / "seed_data"
    with (seed_dir / "generation_models.json").open(encoding="utf-8") as file_handle:
        models = json.load(file_handle)
    with (seed_dir / "workflows.json").open(encoding="utf-8") as file_handle:
        workflows = json.load(file_handle)
    with (seed_dir / "api_library.json").open(encoding="utf-8") as file_handle:
        apis = json.load(file_handle)

    workflow_ids = {model["workflow_id"] for model in models if model.get("workflow_id")}
    assert {workflow["id"] for workflow in workflows} == workflow_ids

    api_ids = {
        node["api_id"]
        for workflow in workflows
        for node in (workflow.get("nodes") or [])
        if node.get("type") == "api_call" and node.get("api_id") is not None
    }
    assert {api["id"] for api in apis} == api_ids
