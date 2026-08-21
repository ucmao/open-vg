"""Admin API routes for workflow management."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List

from ..models.base import get_db
from ..models.admin import Admin
from ..models.workflow import Workflow
from ..models.generation_model import APILibrary
from ..models.generate_page import GeneratePage
from ..models.schemas import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    WorkflowNode,
    WorkflowEdge,
)
from ..utils.auth import get_current_admin
from ..utils.responses import success_response, error_response, paginated_response
from ..utils.logger import logger
from ..services.workflow_executor import WorkflowExecutor

router = APIRouter()
def ensure_work_type_allowed(db: Session, work_type: str) -> None:
    """
    Ensure the given work_type exists as a level-1 generate page.
    This binds workflow.work_type to /generate Category。
    """
    if not work_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="work_type is required",
        )

    exists = (
        db.query(GeneratePage)
        .filter(
            GeneratePage.level == 1,
            GeneratePage.category_name == work_type,
        )
        .first()
    )
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"work_type '{work_type}' must be one of level-1 generate pages (category_name)",
        )



@router.get("/workflows")
def get_workflows(
    work_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all workflows, optionally filtered by work_type, is_active, and search."""
    try:
        query = db.query(Workflow)
        
        if work_type:
            query = query.filter(Workflow.work_type == work_type)
        
        if is_active is not None:
            active_val = True if str(is_active).lower() in ['true', '1', 't', 'y', 'yes'] else False
            query = query.filter(Workflow.is_active == active_val)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Workflow.name.ilike(search_filter),
                    Workflow.description.ilike(search_filter)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated workflows
        workflows = query.order_by(
            Workflow.work_type,
            Workflow.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [workflow.to_full_dict() for workflow in workflows]
        
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            message="Workflows retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        return error_response(
            message="An error occurred while retrieving workflows",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/workflows/{workflow_id}")
def get_workflow(
    workflow_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get a specific workflow by ID."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            logger.warning(f"Workflow {workflow_id} not found")
            return error_response(
                message="Workflow not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Try to serialize the workflow
        try:
            workflow_dict = workflow.to_full_dict()
        except Exception as serialize_error:
            logger.error(f"Error serializing workflow {workflow_id}: {str(serialize_error)}")
            import traceback
            logger.error(traceback.format_exc())
            return error_response(
                message=f"Error serializing workflow: {str(serialize_error)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return success_response(
            data=workflow_dict,
            message="Workflow retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"An error occurred while retrieving workflow: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/workflows/{workflow_id}/params")
def get_workflow_params(
    workflow_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get user-visible params + defaults for a workflow (same as model.params for a model using this workflow)."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return error_response(message="Workflow not found", status_code=status.HTTP_404_NOT_FOUND)
        params = workflow.get_user_visible_params()
        return success_response(data=params or {}, message="Workflow params retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id} params: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return error_response(
            message=f"An error occurred while retrieving workflow params: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/workflows")
def create_workflow(
    request: CreateWorkflowRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new workflow."""
    try:
        # Validate work_type against generate_pages Category
        ensure_work_type_allowed(db, request.work_type)

        # Validate nodes - ensure all api_id references exist
        for node in request.nodes:
            if node.type == "api_call":
                api = db.query(APILibrary).filter(APILibrary.id == node.api_id).first()
                if not api:
                    return error_response(
                        message=f"API Library not found: {node.api_id}",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
        
        # Validate edges - ensure all node references exist
        node_ids = {node.id for node in request.nodes}
        for edge in request.edges:
            if edge.source not in node_ids:
                return error_response(
                    message=f"Edge source node not found: {edge.source}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            if edge.target not in node_ids:
                return error_response(
                    message=f"Edge target node not found: {edge.target}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Create workflow
        workflow_data = {
            "name": request.name,
            "description": request.description,
            "work_type": request.work_type,
            "nodes": [node.model_dump() for node in request.nodes],
            "edges": [edge.model_dump() for edge in request.edges],
            "viewport": request.viewport,
            "is_active": request.is_active,
            "created_by": current_admin.id
        }
        
        new_workflow = Workflow(**workflow_data)
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        
        # Invalidate models cache since workflow changes affect model parameters
        from ..models.generation_config import invalidate_cache
        invalidate_cache()
        
        return success_response(
            data=new_workflow.to_full_dict(),
            message="Workflow created successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workflow: {str(e)}")
        return error_response(
            message="An error occurred while creating workflow",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.put("/workflows/{workflow_id}")
def update_workflow(
    workflow_id: int,
    request: UpdateWorkflowRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a workflow."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            return error_response(
                message="Workflow not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Validate nodes if provided
        if request.nodes is not None:
            node_ids = {node.id for node in request.nodes}
            for node in request.nodes:
                if node.type == "api_call":
                    api = db.query(APILibrary).filter(APILibrary.id == node.api_id).first()
                    if not api:
                        return error_response(
                            message=f"API Library not found: {node.api_id}",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
            
            # Validate edges if provided
            if request.edges is not None:
                for edge in request.edges:
                    if edge.source not in node_ids:
                        return error_response(
                            message=f"Edge source node not found: {edge.source}",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    if edge.target not in node_ids:
                        return error_response(
                            message=f"Edge target node not found: {edge.target}",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
        
        # If work_type is being updated, validate against generate_pages Category
        if request.work_type is not None:
            ensure_work_type_allowed(db, request.work_type)

        # Update fields
        update_data = request.dict(exclude_unset=True)
        
        # Convert Pydantic models to dicts for JSON fields
        if "nodes" in update_data and request.nodes:
            update_data["nodes"] = [node.model_dump() for node in request.nodes]
        if "edges" in update_data and request.edges is not None:
            update_data["edges"] = [edge.model_dump() for edge in request.edges]
        
        for key, value in update_data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        
        db.commit()
        db.refresh(workflow)
        
        # Invalidate models cache since workflow changes affect model parameters
        from ..models.generation_config import invalidate_cache
        invalidate_cache()
        
        return success_response(
            data=workflow.to_full_dict(),
            message="Workflow updated successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating workflow: {str(e)}")
        return error_response(
            message="An error occurred while updating workflow",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a workflow."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            return error_response(
                message="Workflow not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check if any models are using this workflow
        from ..models.generation_model import GenerationModel
        models_using_workflow = db.query(GenerationModel).filter(
            GenerationModel.workflow_id == workflow_id
        ).count()
        
        if models_using_workflow > 0:
            return error_response(
                message=f"Cannot delete workflow: {models_using_workflow} model(s) are using it",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        db.delete(workflow)
        db.commit()
        
        # Invalidate models cache since workflow deletion affects model parameters
        from ..models.generation_config import invalidate_cache
        invalidate_cache()
        
        return success_response(
            message="Workflow deleted successfully"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting workflow: {str(e)}")
        return error_response(
            message="An error occurred while deleting workflow",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/workflows/{workflow_id}/duplicate")
def duplicate_workflow(
    workflow_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Duplicate a workflow."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            return error_response(
                message="Workflow not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Generate a unique name for the duplicate
        base_name = f"{workflow.name} ()"
        new_name = base_name
        counter = 1
        
        # Check if name already exists, append number if needed
        while db.query(Workflow).filter(Workflow.name == new_name).first():
            new_name = f"{workflow.name} ( {counter})"
            counter += 1
        
        # Create a copy of the workflow with a new name
        import copy
        workflow_data = {
            "name": new_name,
            "description": workflow.description,
            "work_type": workflow.work_type,
            "nodes": copy.deepcopy(workflow.nodes) if workflow.nodes else [],
            "edges": copy.deepcopy(workflow.edges) if workflow.edges else [],
            "viewport": copy.deepcopy(workflow.viewport) if workflow.viewport else None,
            "is_active": False,  # New workflow is inactive by default
            "created_by": current_admin.id
        }
        
        new_workflow = Workflow(**workflow_data)
        db.add(new_workflow)
        db.commit()
        db.refresh(new_workflow)
        
        # Invalidate models cache since workflow changes affect model parameters
        from ..models.generation_config import invalidate_cache
        invalidate_cache()
        
        return success_response(
            data=new_workflow.to_full_dict(),
            message="Workflow duplicated successfully",
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error duplicating workflow: {str(e)}")
        return error_response(
            message="An error occurred while duplicating workflow",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/workflows/{workflow_id}/validate")
def validate_workflow(
    workflow_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Validate a workflow configuration."""
    try:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        
        if not workflow:
            return error_response(
                message="Workflow not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        errors = []
        warnings = []
        
        # Validate nodes
        if not workflow.nodes or len(workflow.nodes) == 0:
            errors.append("Workflow must have at least one node")
        
        node_ids = set()
        for node in workflow.nodes:
            node_id = node.get("id")
            if not node_id:
                errors.append("Node missing ID")
                continue
            
            if node_id in node_ids:
                errors.append(f"Duplicate node ID: {node_id}")
            node_ids.add(node_id)
            
            if node.get("type") == "api_call":
                api_id = node.get("api_id")
                if not api_id:
                    errors.append(f"Node {node_id} missing api_id")
                else:
                    api = db.query(APILibrary).filter(APILibrary.id == api_id).first()
                    if not api:
                        errors.append(f"Node {node_id} references non-existent API: {api_id}")
        
        # Validate edges
        if workflow.edges:
            for edge in workflow.edges:
                source = edge.get("source")
                target = edge.get("target")
                
                if source not in node_ids:
                    errors.append(f"Edge references non-existent source node: {source}")
                if target not in node_ids:
                    errors.append(f"Edge references non-existent target node: {target}")
        
        # Check for circular dependencies (topological sort)
        if workflow.nodes and workflow.edges:
            from ..services.workflow_executor import WorkflowExecutor
            executor = WorkflowExecutor(db_session=db)
            execution_order = executor._topological_sort(workflow.nodes, workflow.edges)
            
            if not execution_order:
                errors.append("Workflow has circular dependencies")
            elif len(execution_order) != len(workflow.nodes):
                errors.append("Workflow structure is invalid (not all nodes reachable)")
        
        if errors:
            return error_response(
                message="Workflow validation failed",
                errors=errors,
                warnings=warnings,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return success_response(
            data={
                "valid": True,
                "warnings": warnings
            },
            message="Workflow is valid"
        )
    except Exception as e:
        logger.error(f"Error validating workflow: {str(e)}")
        return error_response(
            message="An error occurred while validating workflow",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
