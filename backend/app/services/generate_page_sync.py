"""
Sync a single GenerationModel to/from generate_pages (level-2).
Used when a model is created, updated, or deleted so the generate page URL works without manual sync.
"""
from sqlalchemy.orm import Session

from ..models.generate_page import GeneratePage
from ..utils.logger import logger
from ..utils.url_slug import slugify


def upsert_generate_page_for_model(
    db: Session,
    work_type: str,
    model_key: str,
    name: str,
) -> bool:
    """
    Create or update the level-2 GeneratePage for this model.
    New pages are created with is_active=True. Existing pages only have
    category_name, title, description, display_description updated.
    Returns True if a page was created or updated, False if skipped (e.g. no parent).
    """
    work_type = (work_type or "").strip()
    model_key = (model_key or "").strip()
    name = (name or "").strip()
    if not work_type or not model_key or not name:
        return False

    parent = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.level == 1,
            GeneratePage.category_name == work_type,
        )
        .first()
    )
    if not parent:
        logger.debug(
            f"generate_page_sync: no level-1 generate page for work_type={work_type}, skip upsert"
        )
        return False

    parent_slug = slugify(parent.category_name)
    page_path = f"/generate/{parent_slug}/{model_key}"

    existing = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.parent_id == parent.id,
            GeneratePage.level == 2,
            GeneratePage.page_path == page_path,
        )
        .first()
    )

    display_description = f"Browse all {name} generations"
    title = f"{name} - {parent.category_name} AI generation"
    description = f"Explore {name} {parent.category_name} AI generation templates and models."

    if existing:
        existing.category_name = name
        existing.title = title
        existing.description = description
        existing.display_description = display_description
        logger.info(
            f"generate_page_sync: updated generate page id={existing.id} for {work_type}/{model_key}"
        )
        return True

    new_child = GeneratePage(
        parent_id=parent.id,
        category_name=name,
        level=2,
        sort_order=0,
        page_path=page_path,
        title=title,
        description=description,
        keywords=None,
        display_description=display_description,
        is_active=True,
    )
    db.add(new_child)
    logger.info(
        f"generate_page_sync: created generate page for {work_type}/{model_key}"
    )
    return True


def delete_generate_page_for_model(
    db: Session,
    work_type: str,
    model_key: str,
) -> bool:
    """
    Delete the level-2 GeneratePage for this model if it exists.
    Returns True if a row was deleted, False otherwise.
    """
    work_type = (work_type or "").strip()
    model_key = (model_key or "").strip()
    if not work_type or not model_key:
        return False

    parent = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.level == 1,
            GeneratePage.category_name == work_type,
        )
        .first()
    )
    if not parent:
        return False

    parent_slug = slugify(parent.category_name)
    page_path = f"/generate/{parent_slug}/{model_key}"

    child = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.parent_id == parent.id,
            GeneratePage.level == 2,
            GeneratePage.page_path == page_path,
        )
        .first()
    )
    if not child:
        return False

    db.delete(child)
    logger.info(
        f"generate_page_sync: deleted generate page id={child.id} for {work_type}/{model_key}"
    )
    return True
