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
from ..models.category_page import CategoryPage
from ..models.schemas import (
    CategoryPageResponse,
    CreateCategoryPageRequest,
    UpdateCategoryPageRequest
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response
from ..utils.logger import logger
from ..utils.url_slug import slugify

router = APIRouter()


class BatchImportCategoryRequest(BaseModel):
    categories: List[dict] = Field(..., description="List of category page objects to import")


@router.get("/category-pages")
async def get_all_category_pages(
    tree: bool = False,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get all category page configurations.
    If tree=True, returns hierarchical tree structure.
    Note: Admin endpoint shows all categories regardless of is_active status.
    """
    try:
        if tree:
            # Return tree structure - admin should see all categories
            parent_categories = db.query(CategoryPage).filter(
                CategoryPage.parent_id == None
            ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
            
            tree_data = []
            for parent in parent_categories:
                parent_dict = parent.to_dict(include_children=False)
                # Get children - admin should see all children regardless of is_active
                children = db.query(CategoryPage).filter(
                    CategoryPage.parent_id == parent.id
                ).order_by(CategoryPage.sort_order, CategoryPage.category_name).all()
                parent_dict["children"] = [child.to_dict(include_children=False) for child in children]
                tree_data.append(parent_dict)
            
            return success_response(
                data=tree_data,
                message="Category pages tree retrieved successfully"
            )
        else:
            # Return flat list
            pages = db.query(CategoryPage).order_by(CategoryPage.level, CategoryPage.sort_order, CategoryPage.category_name).all()
            return success_response(
                data=[page.to_dict(include_children=False) for page in pages],
                message="Category pages retrieved successfully"
            )
    except Exception as e:
        logger.error(f"Error fetching category pages: {e}")
        return error_response(
            message="Failed to fetch category pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/category-pages/{category_name}")
async def get_category_page(
    category_name: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get SEO configuration for a specific category page.
    """
    try:
        page = db.query(CategoryPage).filter(CategoryPage.category_name == category_name).first()
        if not page:
            return error_response(
                message="Category page not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        return success_response(
            data=page.to_dict(),
            message="Category page retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error fetching category page for {category_name}: {e}")
        return error_response(
            message="Failed to fetch category page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/category-pages")
async def create_category_page(
    request: CreateCategoryPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new category page configuration.
    Supports hierarchical structure (level 1 and level 2).
    Automatically generates page_path from category_name if not provided.
    """
    try:
        # Determine level based on parent_id
        level = 1
        parent_id = None
        
        if request.parent_id:
            # Check if parent exists
            parent = db.query(CategoryPage).filter(CategoryPage.id == request.parent_id).first()
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
        page_path = request.page_path
        if not page_path:
            if level == 1:
                page_path = f"/category/{slugify(request.category_name)}"
            else:
                # Level 2: include parent slug
                parent_slug = slugify(parent.category_name)
                child_slug = slugify(request.category_name)
                page_path = f"/category/{parent_slug}/{child_slug}"
        
        # Auto-generate display_description if not provided
        display_description = request.display_description
        if not display_description:
            display_description = f"Browse all {request.category_name} works"
        
        # Create new category page
        new_page = CategoryPage(
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
        
        logger.info(f"Admin {current_admin.username} created category page: {request.category_name} (level {level})")
        
        return success_response(
            data=new_page.to_dict(include_children=False),
            message="Category page created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating category page: {e}")
        return error_response(
            message="Failed to create category page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/category-pages/{category_id}")
async def update_category_page(
    category_id: int,
    request: UpdateCategoryPageRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update configuration for a specific category page.
    Supports updating parent_id to move categories between levels.
    """
    try:
        page = db.query(CategoryPage).filter(CategoryPage.id == category_id).first()
        if not page:
            return error_response(
                message="Category page not found",
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
                    page.page_path = f"/category/{slugify(page.category_name)}"
            else:
                # Moving to level 2
                parent = db.query(CategoryPage).filter(CategoryPage.id == request.parent_id).first()
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
                    page.page_path = f"/category/{parent_slug}/{child_slug}"
        
        # Update category_name if provided
        if request.category_name is not None and request.category_name != page.category_name:
            page.category_name = request.category_name
            # Regenerate page_path if not explicitly provided
            if request.page_path is None:
                if page.level == 1:
                    page.page_path = f"/category/{slugify(request.category_name)}"
                else:
                    parent = db.query(CategoryPage).filter(CategoryPage.id == page.parent_id).first()
                    if parent:
                        parent_slug = slugify(parent.category_name)
                        child_slug = slugify(request.category_name)
                        page.page_path = f"/category/{parent_slug}/{child_slug}"
        
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
        
        logger.info(f"Admin {current_admin.username} updated category page: {page.category_name}")
        
        return success_response(
            data=page.to_dict(include_children=False),
            message="Category page updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating category page {category_id}: {e}")
        return error_response(
            message="Failed to update category page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/category-pages/{category_id}")
async def delete_category_page(
    category_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a category page configuration.
    If deleting a level 1 category, all children will be deleted as well (CASCADE).
    """
    try:
        page = db.query(CategoryPage).filter(CategoryPage.id == category_id).first()
        if not page:
            return error_response(
                message="Category page not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        category_name = page.category_name
        
        # Check if there are works using this category (supports hierarchical categories)
        from ..models.work import Work
        if page.level == 1:
            # Level 1: check for works with this category or any level 2 under it
            works_count = db.query(Work).filter(
                or_(
                    Work.category == category_name,
                    Work.category.like(f"{category_name}|%")
                )
            ).count()
        else:
            # Level 2: exact match only
            works_count = db.query(Work).filter(Work.category == category_name).count()
        
        if works_count > 0:
            return error_response(
                message=f"Cannot delete category: {works_count} works are using this category",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        db.delete(page)
        db.commit()
        
        logger.info(f"Admin {current_admin.username} deleted category page: {category_name}")
        
        return success_response(
            message="Category page deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting category page {category_id}: {e}")
        return error_response(
            message="Failed to delete category page",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/category-pages/batch-import")
async def batch_import_category_pages(
    request: BatchImportCategoryRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Batch import category pages from CSV or JSON data.
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
        level1_map = {}  # category_name -> CategoryPage
        
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
                        page_path = f"/category/{slugify(category_name)}"
                    
                    # Check if exists by page_path (more reliable than category_name)
                    existing = db.query(CategoryPage).filter(
                        CategoryPage.page_path == page_path
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
                            display_description = f"Browse all {category_name} works"
                        
                        new_page = CategoryPage(
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
                logger.error(f"Error processing category row {idx + 1}: {e}")
                continue
        
        # Auto-create missing parent categories from database or create new ones
        for parent_name in needed_parents:
            if parent_name not in level1_map:
                # Check if exists in database
                existing_parent = db.query(CategoryPage).filter(
                    CategoryPage.category_name == parent_name,
                    CategoryPage.level == 1
                ).first()
                
                if existing_parent:
                    level1_map[parent_name] = existing_parent
                else:
                    # Auto-create missing parent category
                    parent_page_path = f"/category/{slugify(parent_name)}"
                    new_parent = CategoryPage(
                        parent_id=None,
                        category_name=parent_name,
                        level=1,
                        sort_order=0,
                        page_path=parent_page_path,
                        title=None,
                        description=None,
                        keywords=None,
                        display_description=f"Browse all {parent_name} works",
                        is_active=False,
                        show_in_explore=False
                    )
                    db.add(new_parent)
                    db.flush()  # Get ID
                    level1_map[parent_name] = new_parent
                    created_count += 1
                    logger.info(f"Auto-created missing parent category: {parent_name}")
        
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
                    # This should not happen after auto-creation, but handle it gracefully
                    errors.append(f"Row {idx + 1}: Parent category '{parent_category_name}' not found (should have been auto-created)")
                    continue
                
                # Generate page_path for level 2
                page_path = category_data.get('page_path', '').strip()
                if not page_path:
                    parent_slug = slugify(parent.category_name)
                    child_slug = slugify(category_name)
                    page_path = f"/category/{parent_slug}/{child_slug}"
                
                # Check if exists by page_path
                existing = db.query(CategoryPage).filter(
                    CategoryPage.page_path == page_path
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
                        display_description = f"Browse all {category_name} works"
                    
                    new_page = CategoryPage(
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
                logger.error(f"Error processing category row {idx + 1}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Admin {current_admin.username} batch imported categories: {created_count} created, {updated_count} updated")
        
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
        logger.error(f"Error in batch import: {e}")
        return error_response(
            message="Failed to batch import category pages",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/category-pages/parse-excel")
async def parse_excel_file(
    file: UploadFile = File(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Parse Excel/CSV file and return preview data.
    Used for frontend preview before batch import.
    """
    try:
        # Read file content
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
        
        # Parse file
        rows = []
        try:
            if file_ext in ['xlsx', 'xls']:
                df = pd.read_excel(BytesIO(content))
                rows = df.to_dict('records')
            else:
                # CSV
                content_str = content.decode('utf-8-sig')  # Handle BOM
                csv_reader = csv.DictReader(content_str.splitlines())
                rows = list(csv_reader)
        except Exception as e:
            logger.error(f"Failed to parse file: {str(e)}")
            return error_response(
                message=f"Failed to parse file: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not rows:
            return error_response(
                message="File is empty or has no valid rows",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Normalize column names (case-insensitive, support both Chinese and English)
        normalized_rows = []
        for row in rows:
            normalized_row = {}
            for key, value in row.items():
                key_lower = key.lower().strip()
                # Map to standard column names
                if key_lower in ['parent_category_name', 'parentcategoryname', 'parent_category', 'Category', 'Category']:
                    normalized_row['parent_category_name'] = str(value).strip() if value else ''
                elif key_lower in ['category_name', 'categoryname', 'Category']:
                    normalized_row['category_name'] = str(value).strip() if value else ''
                elif key_lower in ['title', 'Title']:
                    normalized_row['title'] = str(value).strip() if value else ''
                elif key_lower in ['description', 'Description']:
                    normalized_row['description'] = str(value).strip() if value else ''
                elif key_lower in ['keywords', 'Keywords']:
                    normalized_row['keywords'] = str(value).strip() if value else ''
                elif key_lower in ['display_description', 'displaydescription', 'Description']:
                    normalized_row['display_description'] = str(value).strip() if value else ''
                elif key_lower in ['page_path', 'pagepath', 'Page path']:
                    normalized_row['page_path'] = str(value).strip() if value else ''
                elif key_lower in ['sort_order', 'sortorder', 'Sort order']:
                    normalized_row['sort_order'] = str(value).strip() if value else '0'
                elif key_lower in ['is_active', 'isactive', 'Enable']:
                    normalized_row['is_active'] = str(value).strip() if value else 'false'
                elif key_lower in ['show_in_explore', 'showinexplore', 'Show in explore']:
                    normalized_row['show_in_explore'] = str(value).strip() if value else 'false'
            
            # Only include rows with category_name
            if normalized_row.get('category_name'):
                normalized_rows.append(normalized_row)
        
        return success_response(
            data=normalized_rows,
            message=f"Successfully parsed {len(normalized_rows)} rows"
        )
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"Failed to parse file: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
