"""
用户相关API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserResponse, UserUpdate, UserStatsResponse,
    UserRegister, UserLogin, TokenResponse
)
from app.services import user_service
from app.core.auth import verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/api/user", tags=["用户"])


# ==================== 新版认证API ====================

@router.post("/register", response_model=ApiResponse[TokenResponse])
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册

    - 用户名唯一
    - 密码自动加密
    - 注册成功返回Token
    """
    # 检查用户名是否已存在
    existing = user_service.get_user_by_username(db, request.username)
    if existing:
        return ApiResponse(
            success=False,
            data=None,
            message="用户名已存在"
        )

    # 创建用户
    user = user_service.create_user_with_password(
        db,
        username=request.username,
        password=request.password,
        name=request.name
    )

    # 生成Token
    token = create_access_token({"sub": user.id})

    return ApiResponse(
        data=TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        ),
        message="注册成功"
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    - 验证用户名和密码
    - 返回Token
    """
    user = user_service.get_user_by_username(db, request.username)

    if not user or not user.password_hash:
        return ApiResponse(
            success=False,
            data=None,
            message="用户名或密码错误"
        )

    if not verify_password(request.password, user.password_hash):
        return ApiResponse(
            success=False,
            data=None,
            message="用户名或密码错误"
        )

    # 生成Token
    token = create_access_token({"sub": user.id})

    return ApiResponse(
        data=TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user)
        ),
        message="登录成功"
    )


@router.post("/logout", response_model=ApiResponse[None])
async def logout():
    """
    退出登录

    客户端清除本地Token即可
    """
    return ApiResponse(message="退出成功")


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息（需要认证）
    """
    return ApiResponse(data=UserResponse.model_validate(current_user))


@router.get("/stats/me", response_model=ApiResponse[UserStatsResponse])
async def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户统计数据（需要认证）"""
    import time
    t_start = time.time()

    # 使用用户ID查询统计
    from app.services.record_service import get_month_record_days_by_user_id

    this_month_days = get_month_record_days_by_user_id(db, current_user.id)

    today = datetime.now()
    days_in_month = today.day
    this_month_percentage = round(this_month_days / days_in_month * 100, 1) if days_in_month > 0 else 0

    t_end = time.time()
    print(f"📊 [/user/stats/me] 耗时: {t_end-t_start:.2f}秒", flush=True)

    return ApiResponse(data=UserStatsResponse(
        total_record_days=current_user.total_record_days,
        total_voice_count=current_user.total_voice_count,
        continuous_days=current_user.continuous_days,
        longest_continuous_days=current_user.longest_continuous_days,
        this_month_days=this_month_days,
        this_month_percentage=this_month_percentage
    ))


@router.put("/profile/me", response_model=ApiResponse[UserResponse])
async def update_current_user_profile(
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息（需要认证）
    """
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)

    return ApiResponse(
        data=UserResponse.model_validate(current_user),
        message="更新成功"
    )
