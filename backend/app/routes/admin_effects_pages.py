from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from pydantic import BaseModel, Field
import pandas as pd
from io import BytesIO
import csv

from ..models.base import get_db
from ..models.admin import Admin
from ..models.effects_page import EffectsPage
from ..models.schemas import (
    EffectsPageResponse,
    CreateEffectsPageRequest,
    UpdateEffectsPageRequest
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.url_slug import slugify

router = APIRouter()


class BatchImportEffectsRequest(BaseModel):
    categories: List[dict] = Field(..., description="List of effects page objects to import")


@router.get("/effects-pages")
def get_all_effects_pages(
    tree: bool = False,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all effects page configurations.
    If tree=True, returns hierarchical tree structure.
    Note: Admin endpoint shows all categories regardless of is_active status.
    """
    try:
        if tree:
            # Return tree structure - admin should see all categories
            parent_categories = db.query(EffectsPage).filter(
                EffectsPage.parent_id == None
            ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
            
            tree_data = []
            for parent in parent_categories:
                parent_dict = parent.to_dict(include_children=False)
                # Get children - admin should see all children regardless of is_active
                children = db.query(EffectsPage).filter(
                    EffectsPage.parent_id == parent.id
                ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
                parent_dict["children"] = [child.to_dict(include_children=False) for child in children]
                tree_data.append(parent_dict)
            
            return success_response(
                data=tree_data,
                message="Effects pages tree retrieved successfully"
            )
        else:
            # Return flat list
            pages = db.query(EffectsPage).order_by(EffectsPage.level, EffectsPage.sort_order, EffectsPage.category_name).all()
            return success_response(
                data=[page.to_dict(include_children=False) for page in pages],
                message="Effects pages retrieved successfully"
            )
    except Exception as e:
        logger.error(f"Error fetching effects pages: {e}")
        return error_response(
            message="Failed to fetch effects pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/effects-pages/available-categories")
def get_available_effects_categories(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get categories from generation_models table to help with initial setup.
    Returns unique values from GenerationModel.category column.
    """
    try:
        from ..models.generation_model import GenerationModel
        categories = db.query(GenerationModel.category).filter(
            GenerationModel.category != None,
            GenerationModel.category != ""
        ).distinct().all()
        
        # categories is a list of tuples like [('VFX',), ('3D',)]
        result = [cat[0] for cat in categories]
        
        return success_response(
            data=result,
            message="Available categories from models retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching available model categories: {e}")
        return error_response(
            message="Failed to fetch available categories",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/effects-pages/{category_name}")
def get_effects_page(
    category_name: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get SEO configuration for a specific effects page.
    """
    try:
        page = db.query(EffectsPage).filter(EffectsPage.category_name == category_name).first()
        if not page:
            return error_response(
                message="Effects page not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return success_response(
            data=page.to_dict(),
            message="Effects page retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching effects page for {category_name}: {e}")
        return error_response(
            message="Failed to fetch effects page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/effects-pages")
def create_effects_page(
    request: CreateEffectsPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new effects page configuration.
    Supports hierarchical structure (level 1 and level 2).
    Automatically generates page_path from category_name if not provided.
    """
    try:
        # Determine level based on parent_id
        level = 1
        parent_id = None
        
        if request.parent_id:
            # Check if parent exists
            parent = db.query(EffectsPage).filter(EffectsPage.id == request.parent_id).first()
            if not parent:
                return error_response(
                    message="Parent category not found",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if parent.level != 1:
                return error_response(
                    message="Parent category must be level 1",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            level = 2
            parent_id = request.parent_id
        
        # Auto-generate page_path from category_name if not provided
        # Updated to include /effects/ prefix as requested: /effects/level1/level2
        page_path = request.page_path
        if not page_path:
            if level == 1:
                page_path = f"/effects/{slugify(request.category_name)}"
            else:
                # Level 2: include parent slug
                parent_slug = slugify(parent.category_name)
                child_slug = slugify(request.category_name)
                page_path = f"/effects/{parent_slug}/{child_slug}"
        
        # Auto-generate display_description if not provided
        display_description = request.display_description
        if not display_description:
            display_description = f"Browse all {request.category_name} effects"
        
        # Create new effects page
        new_page = EffectsPage(
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
            show_in_explore=request.show_in_explore if request.show_in_explore is not None else False
        )
        
        db.add(new_page)
        db.commit()
        db.refresh(new_page)
        
        logger.info(f"Admin {current_admin.username} created effects page: {request.category_name} (level {level})")
        
        return success_response(
            data=new_page.to_dict(include_children=False),
            message="Effects page created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating effects page: {e}")
        return error_response(
            message="Failed to create effects page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/effects-pages/{category_id}")
def update_effects_page(
    category_id: int,
    request: UpdateEffectsPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update configuration for a specific effects page.
    Supports updating parent_id to move categories between levels.
    """
    try:
        page = db.query(EffectsPage).filter(EffectsPage.id == category_id).first()
        if not page:
            return error_response(
                message="Effects page not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Handle parent_id change (moving between levels)
        if request.parent_id is not None and request.parent_id != page.parent_id:
            if request.parent_id == 0:
                # Moving to level 1
                page.parent_id = None
                page.level = 1
                # Regenerate page_path
                if not request.page_path:
                    page.page_path = f"/effects/{slugify(page.category_name)}"
            else:
                # Moving to level 2
                parent = db.query(EffectsPage).filter(EffectsPage.id == request.parent_id).first()
                if not parent:
                    return error_response(
                        message="Parent category not found",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                if parent.level != 1:
                    return error_response(
                        message="Parent category must be level 1",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                page.parent_id = request.parent_id
                page.level = 2
                # Regenerate page_path
                if not request.page_path:
                    parent_slug = slugify(parent.category_name)
                    child_slug = slugify(page.category_name)
                    page.page_path = f"/effects/{parent_slug}/{child_slug}"
        
        # Update category_name if provided
        if request.category_name is not None and request.category_name != page.category_name:
            page.category_name = request.category_name
            # Regenerate page_path if not explicitly provided
            if request.page_path is None:
                if page.level == 1:
                    page.page_path = f"/effects/{slugify(request.category_name)}"
                else:
                    parent = db.query(EffectsPage).filter(EffectsPage.id == page.parent_id).first()
                    if parent:
                        parent_slug = slugify(parent.category_name)
                        child_slug = slugify(request.category_name)
                        page.page_path = f"/effects/{parent_slug}/{child_slug}"
        
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
        if request.show_in_explore is not None:
            page.show_in_explore = request.show_in_explore
            
        db.commit()
        db.refresh(page)
        
        logger.info(f"Admin {current_admin.username} updated effects page: {page.category_name}")
        
        return success_response(
            data=page.to_dict(include_children=False),
            message="Effects page updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating effects page {category_id}: {e}")
        return error_response(
            message="Failed to update effects page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/effects-pages/{category_id}")
def delete_effects_page(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete an effects page configuration.
    If deleting a level 1 category, all children will be deleted as well (CASCADE).
    """
    try:
        page = db.query(EffectsPage).filter(EffectsPage.id == category_id).first()
        if not page:
            return error_response(
                message="Effects page not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        category_name = page.category_name
        
        # In this case, we don't strictly check for works usage as effects are handled differently
        # But we could check generation_models.category if needed
        
        db.delete(page)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} deleted effects page: {category_name}")
        
        return success_response(
            message="Effects page deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting effects page {category_id}: {e}")
        return error_response(
            message="Failed to delete effects page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/effects-pages/batch-import")
def batch_import_effects_pages(
    request: BatchImportEffectsRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch import effects pages from CSV or JSON data.
    Supports hierarchical structure with parent_category_name field.
    Creates new pages or updates existing ones based on category_name and page_path.
    """
    try:
        created_count = 0
        updated_count = 0
        errors = []
        
        # First pass: collect all parent category names that are needed
        needed_parents = set()
        for category_data in request.categories:
            parent_category_name = category_data.get('parent_category_name', '').strip()
            if parent_category_name:
                needed_parents.add(parent_category_name)
        
        # First pass: create/update level 1 categories
        level1_map = {}  # category_name -> EffectsPage
        
        for idx, category_data in enumerate(request.categories):
            try:
                parent_category_name = category_data.get('parent_category_name', '').strip()
                category_name = category_data.get('category_name', '').strip()
                
                if not category_name:
                    errors.append(f"Row {idx + 1}: category_name is required")
                    continue
                
                # If no parent, it's level 1
                if not parent_category_name:
                    page_path = category_data.get('page_path', '').strip()
                    if not page_path:
                        page_path = f"/effects/{slugify(category_name)}"
                    
                    # Check if exists by page_path
                    existing = db.query(EffectsPage).filter(
                        EffectsPage.page_path == page_path
                    ).first()
                    
                    if existing:
                        # Update existing
                        if 'title' in category_data:
                            existing.title = category_data.get('title', '').strip() or None
                        if 'description' in category_data:
                            existing.description = category_data.get('description', '').strip() or None
                        if 'keywords' in category_data:
                            existing.keywords = category_data.get('keywords', '').strip() or None
                        if 'display_description' in category_data:
                            existing.display_description = category_data.get('display_description', '').strip() or None
                        if 'sort_order' in category_data:
                            try:
                                existing.sort_order = int(category_data.get('sort_order', 0))
                            except:
                                pass
                        if 'is_active' in category_data:
                            existing.is_active = str(category_data.get('is_active', 'false')).lower() == 'true'
                        if 'show_in_explore' in category_data:
                            existing.show_in_explore = str(category_data.get('show_in_explore', 'false')).lower() == 'true'
                        if category_data.get('page_path'):
                            existing.page_path = page_path
                        level1_map[category_name] = existing
                        updated_count += 1
                    else:
                        # Create new level 1
                        display_description = category_data.get('display_description', '').strip()
                        if not display_description:
                            display_description = f"Browse all {category_name} effects"
                        
                        new_page = EffectsPage(
                            parent_id=None,
                            category_name=category_name,
                            level=1,
                            sort_order=int(category_data.get('sort_order', 0)) if category_data.get('sort_order') else 0,
                            page_path=page_path,
                            title=category_data.get('title', '').strip() or None,
                            description=category_data.get('description', '').strip() or None,
                            keywords=category_data.get('keywords', '').strip() or None,
                            display_description=display_description or None,
                            is_active=str(category_data.get('is_active', 'false')).lower() == 'true' if category_data.get('is_active') else False,
                            show_in_explore=str(category_data.get('show_in_explore', 'false')).lower() == 'true' if category_data.get('show_in_explore') else False
                        )
                        db.add(new_page)
                        db.flush()  # Get ID
                        level1_map[category_name] = new_page
                        created_count += 1
                        
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                logger.error(f"Error processing effects row {idx + 1}: {e}")
                continue
        
        # Auto-create missing parent categories
        for parent_name in needed_parents:
            if parent_name not in level1_map:
                # Check if exists in database
                existing_parent = db.query(EffectsPage).filter(
                    EffectsPage.category_name == parent_name,
                    EffectsPage.level == 1
                ).first()
                
                if existing_parent:
                    level1_map[parent_name] = existing_parent
                else:
                    # Auto-create missing parent category
                    parent_page_path = f"/effects/{slugify(parent_name)}"
                    new_parent = EffectsPage(
                        parent_id=None,
                        category_name=parent_name,
                        level=1,
                        sort_order=0,
                        page_path=parent_page_path,
                        title=None,
                        description=None,
                        keywords=None,
                        display_description=f"Browse all {parent_name} effects",
                        is_active=False,
                        show_in_explore=False
                    )
                    db.add(new_parent)
                    db.flush()  # Get ID
                    level1_map[parent_name] = new_parent
                    created_count += 1
                    logger.info(f"Auto-created missing parent effects category: {parent_name}")
        
        # Second pass: create/update level 2 categories
        for idx, category_data in enumerate(request.categories):
            try:
                parent_category_name = category_data.get('parent_category_name', '').strip()
                category_name = category_data.get('category_name', '').strip()
                
                if not category_name or not parent_category_name:
                    continue  # Skip level 1 categories in second pass
                
                # Find parent
                parent = level1_map.get(parent_category_name)
                if not parent:
                    errors.append(f"Row {idx + 1}: Parent category '{parent_category_name}' not found")
                    continue
                
                # Generate page_path for level 2
                page_path = category_data.get('page_path', '').strip()
                if not page_path:
                    parent_slug = slugify(parent.category_name)
                    child_slug = slugify(category_name)
                    page_path = f"/effects/{parent_slug}/{child_slug}"
                
                # Check if exists by page_path
                existing = db.query(EffectsPage).filter(
                    EffectsPage.page_path == page_path
                ).first()
                
                if existing:
                    # Update existing
                    if 'title' in category_data:
                        existing.title = category_data.get('title', '').strip() or None
                    if 'description' in category_data:
                        existing.description = category_data.get('description', '').strip() or None
                    if 'keywords' in category_data:
                        existing.keywords = category_data.get('keywords', '').strip() or None
                    if 'display_description' in category_data:
                        existing.display_description = category_data.get('display_description', '').strip() or None
                    if 'sort_order' in category_data:
                        try:
                            existing.sort_order = int(category_data.get('sort_order', 0))
                        except:
                            pass
                    if 'is_active' in category_data:
                        existing.is_active = str(category_data.get('is_active', 'true')).lower() == 'true'
                    if category_data.get('page_path'):
                        existing.page_path = page_path
                    # Ensure parent_id is correct
                    existing.parent_id = parent.id
                    existing.level = 2
                    updated_count += 1
                else:
                    # Create new level 2
                    display_description = category_data.get('display_description', '').strip()
                    if not display_description:
                        display_description = f"Browse all {category_name} effects"
                    
                    new_page = EffectsPage(
                        parent_id=parent.id,
                        category_name=category_name,
                        level=2,
                        sort_order=int(category_data.get('sort_order', 0)) if category_data.get('sort_order') else 0,
                        page_path=page_path,
                        title=category_data.get('title', '').strip() or None,
                        description=category_data.get('description', '').strip() or None,
                        keywords=category_data.get('keywords', '').strip() or None,
                        display_description=display_description or None,
                        is_active=str(category_data.get('is_active', 'false')).lower() == 'true' if category_data.get('is_active') else False,
                        show_in_explore=str(category_data.get('show_in_explore', 'false')).lower() == 'true' if category_data.get('show_in_explore') else False
                    )
                    db.add(new_page)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
                logger.error(f"Error processing effects row {idx + 1}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} batch imported effects: {created_count} created, {updated_count} updated")
        
        return success_response(
            data={
                "created": created_count,
                "updated": updated_count,
                "total": len(request.categories),
                "errors": errors if errors else None
            },
            message=f"Batch import completed: {created_count} created, {updated_count} updated"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch import effects: {e}")
        return error_response(
            message="Failed to batch import effects pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/effects-pages/by-path/{page_path:path}")
def get_effects_page_by_path(
    page_path: str,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to get effects page SEO configuration by its path.
    Example path: /effects/lala or /effects/lala/ccc
    """
    try:
        from sqlalchemy.orm import joinedload
        
        # Normalize path - ensure starts with /
        full_path = page_path if page_path.startswith('/') else f"/{page_path}"
        
        # If path is just /effects, try to find a root effects page or return a default
        if full_path == "/effects":
            # You might want to return a general effects page config here
            # For now, let's try to find if there's an entry for /effects
            page = db.query(EffectsPage).filter(
                EffectsPage.page_path == "/effects",
                EffectsPage.is_active == True
            ).first()
            if not page:
                # Return a default structure if not found in DB
                return success_response(
                    data={
                        "category_name": "Effects",
                        "level": 0,
                        "page_path": "/effects",
                        "title": "AI Video Effects & Templates",
                        "description": "Explore our collection of AI generation models and their amazing effects.",
                        "is_active": True
                    }
                )
        else:
            # Load page with parent relationship eagerly
            page = db.query(EffectsPage).options(
                joinedload(EffectsPage.parent)
            ).filter(
                EffectsPage.page_path == full_path,
                EffectsPage.is_active == True
            ).first()
        
        if not page:
            return error_response(
                message="Effects page not found or inactive",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        return success_response(
            data=page.to_dict(include_parent=True),
            message="Effects page retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching effects page by path {page_path}: {e}")
        return error_response(
            message="Failed to fetch effects page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/effects-pages/{category_id}/children")
def get_effects_page_children(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to get children of an effects page.
    """
    try:
        children = db.query(EffectsPage).filter(
            EffectsPage.parent_id == category_id,
            EffectsPage.is_active == True
        ).order_by(EffectsPage.sort_order, EffectsPage.category_name).all()
        
        return success_response(
            data=[child.to_dict(include_children=False) for child in children],
            message="Children categories retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching effects page children for {category_id}: {e}")
        return error_response(
            message="Failed to fetch children categories",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

