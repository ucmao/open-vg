from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Return a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized format
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    
    return JSONResponse(content=response, status_code=status_code)


def error_response(
    message: str = "An error occurred",
    errors: Optional[dict] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Return a standardized error response.
    
    Args:
        message: Error message
        errors: Optional detailed errors dictionary
        status_code: HTTP status code
        
    Returns:
        JSONResponse with standardized format
    """
    response = {
        "success": False,
        "message": message,
    }
    
    if errors:
        response["errors"] = errors
    
    return JSONResponse(content=response, status_code=status_code)


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "Success"
) -> JSONResponse:
    """
    Return a standardized paginated response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
        message: Success message
        
    Returns:
        JSONResponse with standardized paginated format
    """
    total_pages = (total + page_size - 1) // page_size
    
    response = {
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
    }
    
    return JSONResponse(content=response, status_code=status.HTTP_200_OK)

