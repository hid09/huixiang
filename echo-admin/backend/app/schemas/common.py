from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""

    code: int = Field(200, description="状态码")
    message: str = Field("", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""

    total: int = Field(..., description="总数量")
    items: list[T] = Field(..., description="数据列表")
