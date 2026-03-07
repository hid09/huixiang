"""
通用响应模型
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    success: bool = True
    data: Optional[T] = None
    message: str = "操作成功"

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {},
                "message": "操作成功"
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""
    code: int
    message: str


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: ErrorDetail
