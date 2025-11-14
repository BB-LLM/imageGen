"""
图生视频API路由
【已废弃】图像转GIF功能已移除，不再使用SVD模型
"""
from fastapi import APIRouter, HTTPException, status

# 创建空的路由器，避免导入错误
router = APIRouter(prefix="/video", tags=["图生视频（已废弃）"])


# 所有路由已废弃，图像转GIF功能已移除
@router.get("/estimate")
async def estimate_generation_time():
    """已废弃：图像转GIF功能已移除"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="图像转GIF功能已移除，此端点已废弃"
    )


@router.post("/generate")
async def generate_video():
    """已废弃：图像转GIF功能已移除"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="图像转GIF功能已移除，此端点已废弃"
    )


@router.post("/generate-from-variant")
async def generate_video_from_variant():
    """已废弃：图像转GIF功能已移除"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="图像转GIF功能已移除，此端点已废弃"
    )
