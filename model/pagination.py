from pydantic import BaseModel, Field
from typing import List, Generic, TypeVar, Optional, Any

# Define a generic type for the items
T = TypeVar('T')

class PaginationParams(BaseModel):
    """Parameters for pagination"""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return")
    

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[T]
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
    has_more: bool = Field(..., description="Whether there are more items available")
    
    @classmethod
    def create(cls, items: List[T], total: int, skip: int, limit: int) -> 'PaginatedResponse[T]':
        """Create a paginated response"""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items) < total)
        )
