from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple, Set

from ..models.base import get_db
from ..models.admin import Admin
from ..models.generate_page import GeneratePage
from ..models.generation_model import GenerationModel
from ..models.schemas import (
    GeneratePageResponse,
    CreateGeneratePageRequest,
    UpdateGeneratePageRequest,
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.url_slug import slugify

router = APIRouter()


class BatchImportGenerateRequest(CreateGeneratePageRequest):
    categories: List[dict]


@router.get("/generate-pages")
def get_all_generate_pages(
    tree: bool = False,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get all generate page configurations.
    If tree=True, returns hierarchical tree structure.
    Admin （ is_active）。
    """
    try:
        if tree:
            parent_categories = (
                db.query(GeneratePage)
                .filter(GeneratePage.parent_id.is_(None))
                .order_by(GeneratePage.sort_order, GeneratePage.category_name)
                .all()
            )

            tree_data = []
            for parent in parent_categories:
                parent_dict = parent.to_dict(include_children=False)
                children = (
                    db.query(GeneratePage)
                    .filter(GeneratePage.parent_id == parent.id)
                    .order_by(GeneratePage.sort_order, GeneratePage.category_name)
                    .all()
                )
                parent_dict["children"] = [
                    child.to_dict(include_children=False) for child in children
                ]
                tree_data.append(parent_dict)

            return success_response(
                data=tree_data, message="Generate pages tree retrieved successfully"
            )
        else:
            pages = (
                db.query(GeneratePage)
                .order_by(
                    GeneratePage.level,
                    GeneratePage.sort_order,
                    GeneratePage.category_name,
                )
                .all()
            )
            return success_response(
                data=[page.to_dict(include_children=False) for page in pages],
                message="Generate pages retrieved successfully",
            )
    except Exception as e:
        logger.error(f"Error fetching generate pages: {e}")
        return error_response(
            message="Failed to fetch generate pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Category(category_name + sort_order), / work_type
DEFAULT_LEVEL1_CATEGORIES = [
    ("video-effects", 0),
    ("image-effects", 1),
    ("image-to-video", 2),
    ("text-to-video", 3),
    ("image-to-image", 4),
    ("text-to-image", 5),
]


@router.post("/generate-pages/ensure-default-level1")
def ensure_default_level1_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
     6 Category（does not exist）：
    video-effects, image-effects, image-to-video, text-to-video, image-to-image, text-to-image
    """
    try:
        new_pages = []
        for category_name, sort_order in DEFAULT_LEVEL1_CATEGORIES:
            existing = (
                db.query(GeneratePage)
                .filter(
                    GeneratePage.parent_id.is_(None),
                    GeneratePage.category_name == category_name,
                )
                .first()
            )
            if existing:
                continue
            page_path = f"/generate/{slugify(category_name)}"
            readable_name = category_name.replace("-", " ").title()
            title = f"{readable_name} - AI Generation"
            description = f"Explore {readable_name} AI generation tools and models."
            display_description = f"Browse all {category_name} generations"
            new_page = GeneratePage(
                parent_id=None,
                category_name=category_name,
                level=1,
                sort_order=sort_order,
                page_path=page_path,
                title=title,
                description=description,
                keywords=None,
                display_description=display_description,
                is_active=False,
            )
            db.add(new_page)
            new_pages.append(new_page)
        db.commit()
        for p in new_pages:
            db.refresh(p)
        created = [p.to_dict(include_children=False) for p in new_pages]
        logger.info(
            f"Admin {current_admin.username} ensured default level1 categories: {len(created)} created"
        )
        return success_response(
            data={"created": created, "created_count": len(created)},
            message=f" {len(created)} Category" if created else "Categoryalready exists，",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error ensuring default level1 categories: {e}")
        return error_response(
            message="Failed to ensure default level1 categories",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/generate-pages/sync-from-models")
def sync_generate_pages_from_models(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Sync level-2 generate pages from active generation models (weak overwrite).

    （ work_type + model_key slug ， TDK）：
    - Enable：does not exist（ parent + slug）（ TDK，is_active=True）；
      already exists category_name  name， title/description/keywords/is_active。
    - ：， slug  (work_type, model_key)，。
    """
    try:
        # Collect distinct (work_type, model_key, name) triples from models
        rows = (
            db.query(
                GenerationModel.work_type,
                GenerationModel.model_key,
                GenerationModel.name,
            )
            .filter(
                GenerationModel.is_active == True,  # noqa: E712
                GenerationModel.work_type.isnot(None),
                GenerationModel.work_type != "",
                GenerationModel.model_key.isnot(None),
                GenerationModel.model_key != "",
                GenerationModel.name.isnot(None),
                GenerationModel.name != "",
            )
            .distinct()
            .all()
        )

        if not rows:
            return success_response(
                data={"created": 0, "deleted": 0, "updated": 0, "models": 0},
                message="not foundEnable，。",
            )

        models: List[Tuple[str, str, str]] = []
        for work_type, model_key, name in rows:
            wt = (work_type or "").strip()
            mk = (model_key or "").strip()
            nm = (name or "").strip()
            if wt and mk and nm:
                models.append((wt, mk, nm))

        if not models:
            return success_response(
                data={"created": 0, "deleted": 0, "updated": 0, "models": 0},
                message=" (work_type, model_key, name)，。",
            )

        # Preload level-1 generate pages
        parents = (
            db.query(GeneratePage)
            .filter(GeneratePage.level == 1)
            .all()
        )
        parent_map: Dict[str, GeneratePage] = {
            p.category_name: p for p in parents if p.category_name
        }
        parent_ids_to_sync = {
            parent_map[wt].id for wt, _, _ in models if parent_map.get(wt)
        }
        parent_id_to_work_type: Dict[int, str] = {
            p.id: p.category_name for p in parents if p.category_name
        }

        # (work_type, model_key)
        model_slugs_set: Set[Tuple[str, str]] = {(wt, mk) for wt, mk, _ in models}

        # 1) : (parent_work_type, slug) model_slugs_set
        deleted_count = 0
        if parent_ids_to_sync:
            children = (
                db.query(GeneratePage)
                .filter(
                    GeneratePage.level == 2,
                    GeneratePage.parent_id.in_(parent_ids_to_sync),
                )
                .all()
            )
            for child in children:
                work_type = parent_id_to_work_type.get(child.parent_id)
                if work_type is None:
                    continue
                # slug = page_path , /generate/text-to-image/veo-3 -> veo-3
                parts = (child.page_path or "").strip("/").split("/")
                slug = parts[-1] if len(parts) >= 2 else ""
                if (work_type, slug) not in model_slugs_set:
                    db.delete(child)
                    deleted_count += 1

        # 2)  +  category_name
        created_count = 0
        updated_count = 0
        skipped_missing_parent: Set[str] = set()

        for work_type, model_key, name in models:
            parent = parent_map.get(work_type)
            if not parent:
                skipped_missing_parent.add(work_type)
                continue

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

            if existing:
                if existing.category_name != name:
                    existing.category_name = name
                    updated_count += 1
                continue

            display_description = f"Browse all {name} generations"
            title = f"{name} - {parent.category_name} AI generation"
            description = f"Explore {name} {parent.category_name} AI generation templates and models."

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
            created_count += 1

        db.commit()

        logger.info(
            f"Admin {current_admin.username} synced generate pages from models: "
            f"deleted {deleted_count} orphans, created {created_count}, updated name {updated_count}. "
            f"Missing parents: {', '.join(sorted(skipped_missing_parent)) if skipped_missing_parent else 'none'}."
        )

        return success_response(
            data={
                "created": created_count,
                "deleted": deleted_count,
                "updated": updated_count,
                "models": len(models),
                "missing_parents": sorted(skipped_missing_parent),
            },
            message=f"： {deleted_count} ， {created_count} ， {updated_count} （already exists TDK）。",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error syncing generate pages from models: {e}")
        return error_response(
            message="Failed to sync generate pages from models",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/generate-pages/{category_name}")
def get_generate_page(
    category_name: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Get SEO configuration for a specific generate page by category_name.
    """
    try:
        page = (
            db.query(GeneratePage)
            .filter(GeneratePage.category_name == category_name)
            .first()
        )
        if not page:
            return error_response(
                message="Generate page not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return success_response(
            data=page.to_dict(), message="Generate page retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching generate page for {category_name}: {e}")
        return error_response(
            message="Failed to fetch generate page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/generate-pages")
def create_generate_page(
    request: CreateGeneratePageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new generate page configuration.
    Supports hierarchical structure (level 1 and level 2).
    Automatically generates page_path from category_name if not provided.
    """
    try:
        level = 1
        parent_id = None

        parent = None
        if request.parent_id:
            parent = (
                db.query(GeneratePage)
                .filter(GeneratePage.id == request.parent_id)
                .first()
            )
            if not parent:
                return error_response(
                    message="Parent category not found",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if parent.level != 1:
                return error_response(
                    message="Parent category must be level 1",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            level = 2
            parent_id = request.parent_id

        page_path = request.page_path
        if not page_path:
            if level == 1:
                page_path = f"/generate/{slugify(request.category_name)}"
            else:
                parent_slug = slugify(parent.category_name) if parent else ""
                child_slug = slugify(request.category_name)
                page_path = f"/generate/{parent_slug}/{child_slug}"

        display_description = request.display_description
        if not display_description:
            display_description = f"Browse all {request.category_name} generations"

        new_page = GeneratePage(
            parent_id=parent_id,
            category_name=request.category_name,
            level=level,
            sort_order=request.sort_order or 0,
            page_path=page_path,
            title=request.title,
            description=request.description,
            keywords=request.keywords,
            display_description=display_description,
            is_active=request.is_active if request.is_active is not None else False,
        )

        db.add(new_page)
        db.commit()
        db.refresh(new_page)

        logger.info(
          f"Admin {current_admin.username} created generate page: {request.category_name} (level {level})"
        )

        return success_response(
            data=new_page.to_dict(include_children=False),
            message="Generate page created successfully",
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating generate page: {e}")
        return error_response(
            message="Failed to create generate page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.put("/generate-pages/{category_id}")
def update_generate_page(
    category_id: int,
    request: UpdateGeneratePageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update configuration for a specific generate page.
    Supports updating parent_id to move categories between levels.
    """
    try:
        page = (
            db.query(GeneratePage)
            .filter(GeneratePage.id == category_id)
            .first()
        )
        if not page:
            return error_response(
                message="Generate page not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.parent_id is not None and request.parent_id != page.parent_id:
            if request.parent_id == 0:
                page.parent_id = None
                page.level = 1
                if not request.page_path:
                    page.page_path = f"/generate/{slugify(page.category_name)}"
            else:
                parent = (
                    db.query(GeneratePage)
                    .filter(GeneratePage.id == request.parent_id)
                    .first()
                )
                if not parent:
                    return error_response(
                        message="Parent category not found",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                if parent.level != 1:
                    return error_response(
                        message="Parent category must be level 1",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                page.parent_id = request.parent_id
                page.level = 2
                if not request.page_path:
                    parent_slug = slugify(parent.category_name)
                    child_slug = slugify(page.category_name)
                    page.page_path = f"/generate/{parent_slug}/{child_slug}"

        if request.category_name is not None and request.category_name != page.category_name:
            page.category_name = request.category_name
            if request.page_path is None:
                if page.level == 1:
                    page.page_path = f"/generate/{slugify(request.category_name)}"
                else:
                    parent = (
                        db.query(GeneratePage)
                        .filter(GeneratePage.id == page.parent_id)
                        .first()
                    )
                    if parent:
                        parent_slug = slugify(parent.category_name)
                        child_slug = slugify(request.category_name)
                        page.page_path = f"/generate/{parent_slug}/{child_slug}"

        if request.page_path is not None:
            page.page_path = request.page_path
        if request.title is not None:
            page.title = request.title
        if request.description is not None:
            page.description = request.description
        if request.keywords is not None:
            page.keywords = request.keywords
        if request.display_description is not None:
            page.display_description = request.display_description
        if request.sort_order is not None:
            page.sort_order = request.sort_order
        if request.is_active is not None:
            page.is_active = request.is_active

        db.commit()
        db.refresh(page)

        logger.info(f"Admin {current_admin.username} updated generate page: {page.category_name}")

        return success_response(
            data=page.to_dict(include_children=False),
            message="Generate page updated successfully",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating generate page {category_id}: {e}")
        return error_response(
            message="Failed to update generate page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete("/generate-pages/{category_id}")
def delete_generate_page(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Delete a generate page configuration.
    If deleting a level 1 category, explicitly delete all children first, then the parent.
    """
    try:
        page = (
            db.query(GeneratePage)
            .filter(GeneratePage.id == category_id)
            .first()
        )
        if not page:
            return error_response(
                message="Generate page not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        category_name = page.category_name

        # Category( DB CASCADE)
        if page.level == 1:
            children = (
                db.query(GeneratePage)
                .filter(GeneratePage.parent_id == page.id)
                .all()
            )
            for child in children:
                db.delete(child)
            logger.info(
                f"Admin {current_admin.username} deleted {len(children)} level-2 generate page(s) under {category_name}"
            )

        db.delete(page)
        db.commit()

        logger.info(f"Admin {current_admin.username} deleted generate page: {category_name}")

        return success_response(
            message="Generate page deleted successfully",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting generate page {category_id}: {e}")
        return error_response(
            message="Failed to delete generate page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/generate-pages/batch-import")
def batch_import_generate_pages(
    request: BatchImportGenerateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Batch import generate pages from CSV/JSON-like data.
    Supports hierarchical structure with parent_category_name field.
    """
    try:
        created_count = 0
        updated_count = 0
        errors: List[str] = []

        needed_parents = set()
        for category_data in request.categories:
            parent_category_name = category_data.get("parent_category_name", "").strip()
            if parent_category_name:
                needed_parents.add(parent_category_name)

        level1_map = {}

        for idx, category_data in enumerate(request.categories):
            try:
                parent_category_name = category_data.get("parent_category_name", "").strip()
                category_name = category_data.get("category_name", "").strip()

                if not category_name:
                  errors.append(f"Row {idx + 1}: category_name is required")
                  continue

                if not parent_category_name:
                    page_path = category_data.get("page_path", "").strip()
                    if not page_path:
                        page_path = f"/generate/{slugify(category_name)}"

                    existing = (
                        db.query(GeneratePage)
                        .filter(GeneratePage.page_path == page_path)
                        .first()
                    )

                    if existing:
                        for field in ["title", "description", "keywords", "display_description"]:
                            if field in category_data:
                                value = category_data.get(field, "").strip()
                                setattr(existing, field, value or None)

                        if "sort_order" in category_data:
                            try:
                                existing.sort_order = int(category_data.get("sort_order", 0))
                            except Exception:
                                pass

                        if "is_active" in category_data:
                            existing.is_active = (
                                str(category_data.get("is_active", "false")).lower() == "true"
                            )

                        if category_data.get("page_path"):
                            existing.page_path = page_path

                        level1_map[category_name] = existing
                        updated_count += 1
                    else:
                        display_description = category_data.get("display_description", "").strip()
                        if not display_description:
                            display_description = f"Browse all {category_name} generations"

                        new_page = GeneratePage(
                            parent_id=None,
                            category_name=category_name,
                            level=1,
                            sort_order=int(category_data.get("sort_order", 0))
                            if category_data.get("sort_order")
                            else 0,
                            page_path=page_path,
                            title=category_data.get("title", "").strip() or None,
                            description=category_data.get("description", "").strip() or None,
                            keywords=category_data.get("keywords", "").strip() or None,
                            display_description=display_description or None,
                            is_active=str(category_data.get("is_active", "false")).lower()
                            == "true"
                            if category_data.get("is_active")
                            else False,
                        )
                        db.add(new_page)
                        db.flush()
                        level1_map[category_name] = new_page
                        created_count += 1
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                logger.error(f"Error processing generate row {idx + 1}: {e}")
                continue

        for parent_name in needed_parents:
            if parent_name not in level1_map:
                existing_parent = (
                    db.query(GeneratePage)
                    .filter(
                        GeneratePage.category_name == parent_name,
                        GeneratePage.level == 1,
                    )
                    .first()
                )

                if existing_parent:
                    level1_map[parent_name] = existing_parent
                else:
                    parent_page_path = f"/generate/{slugify(parent_name)}"
                    new_parent = GeneratePage(
                        parent_id=None,
                        category_name=parent_name,
                        level=1,
                        sort_order=0,
                        page_path=parent_page_path,
                        title=None,
                        description=None,
                        keywords=None,
                        display_description=f"Browse all {parent_name} generations",
                        is_active=False,
                    )
                    db.add(new_parent)
                    db.flush()
                    level1_map[parent_name] = new_parent
                    created_count += 1
                    logger.info(f"Auto-created missing parent generate category: {parent_name}")

        for idx, category_data in enumerate(request.categories):
            try:
                parent_category_name = category_data.get("parent_category_name", "").strip()
                category_name = category_data.get("category_name", "").strip()

                if not category_name or not parent_category_name:
                    continue

                parent = level1_map.get(parent_category_name)
                if not parent:
                    errors.append(
                        f"Row {idx + 1}: Parent category '{parent_category_name}' not found"
                    )
                    continue

                page_path = category_data.get("page_path", "").strip()
                if not page_path:
                    parent_slug = slugify(parent.category_name)
                    child_slug = slugify(category_name)
                    page_path = f"/generate/{parent_slug}/{child_slug}"

                existing = (
                    db.query(GeneratePage)
                    .filter(GeneratePage.page_path == page_path)
                    .first()
                )

                if existing:
                    for field in ["title", "description", "keywords", "display_description"]:
                        if field in category_data:
                            value = category_data.get(field, "").strip()
                            setattr(existing, field, value or None)

                    if "sort_order" in category_data:
                        try:
                            existing.sort_order = int(category_data.get("sort_order", 0))
                        except Exception:
                            pass

                    if "is_active" in category_data:
                        existing.is_active = (
                            str(category_data.get("is_active", "true")).lower() == "true"
                        )

                    if category_data.get("page_path"):
                        existing.page_path = page_path

                    existing.parent_id = parent.id
                    existing.level = 2
                    updated_count += 1
                else:
                    display_description = category_data.get("display_description", "").strip()
                    if not display_description:
                        display_description = f"Browse all {category_name} generations"

                    new_page = GeneratePage(
                        parent_id=parent.id,
                        category_name=category_name,
                        level=2,
                        sort_order=int(category_data.get("sort_order", 0))
                        if category_data.get("sort_order")
                        else 0,
                        page_path=page_path,
                        title=category_data.get("title", "").strip() or None,
                        description=category_data.get("description", "").strip() or None,
                        keywords=category_data.get("keywords", "").strip() or None,
                        display_description=display_description or None,
                        is_active=str(category_data.get("is_active", "false")).lower()
                        == "true"
                        if category_data.get("is_active")
                        else False,
                    )
                    db.add(new_page)
                    created_count += 1
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                logger.error(f"Error processing generate row {idx + 1}: {e}")
                continue

        db.commit()

        logger.info(
            f"Admin {current_admin.username} batch imported generate pages: {created_count} created, {updated_count} updated"
        )

        return success_response(
            data={
                "created": created_count,
                "updated": updated_count,
                "total": len(request.categories),
                "errors": errors if errors else None,
            },
            message=f"Batch import completed: {created_count} created, {updated_count} updated",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch import generate pages: {e}")
        return error_response(
            message="Failed to batch import generate pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/generate-pages/by-path/{page_path:path}")
def get_generate_page_by_path(
    page_path: str,
    db: Session = Depends(get_db),
):
    """
    Public endpoint to get generate page SEO configuration by its path.
    Example path: /generate/img2video or /generate/img2video/nano-banana-pro
    """
    try:
        from sqlalchemy.orm import joinedload

        full_path = page_path if page_path.startswith("/") else f"/{page_path}"

        if full_path == "/generate":
            page = (
                db.query(GeneratePage)
                .filter(
                    GeneratePage.page_path == "/generate",
                    GeneratePage.is_active.is_(True),
                )
                .first()
            )
            if not page:
                return success_response(
                    data={
                        "category_name": "Generate",
                        "level": 0,
                        "page_path": "/generate",
                        "title": "AI Generation Tools",
                        "description": "Explore our AI generation tools for images and videos.",
                        "is_active": True,
                    }
                )
        else:
            page = (
                db.query(GeneratePage)
                .options(joinedload(GeneratePage.parent))
                .filter(
                    GeneratePage.page_path == full_path,
                    GeneratePage.is_active.is_(True),
                )
                .first()
            )

        if not page:
            return error_response(
                message="Generate page not found or inactive",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            data=page.to_dict(include_parent=True),
            message="Generate page retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error fetching generate page by path {page_path}: {e}")
        return error_response(
            message="Failed to fetch generate page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/generate-pages/{category_id}/children")
def get_generate_page_children(
    category_id: int,
    db: Session = Depends(get_db),
):
    """
    Public endpoint to get children of a generate page.
    """
    try:
        children = (
            db.query(GeneratePage)
            .filter(
                GeneratePage.parent_id == category_id,
                GeneratePage.is_active.is_(True),
            )
            .order_by(GeneratePage.sort_order, GeneratePage.category_name)
            .all()
        )

        return success_response(
            data=[child.to_dict(include_children=False) for child in children],
            message="Generate children categories retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Error fetching generate page children for {category_id}: {e}")
        return error_response(
            message="Failed to fetch children categories",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

