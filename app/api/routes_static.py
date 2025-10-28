"""
静态文件服务 - 提供生成的图像
"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/static", tags=["静态文件"])

# 生成图像目录
GENERATED_IMAGES_DIR = "generated_images"


@router.get("/image/{filename}")
async def get_generated_image(filename: str):
    """
    获取生成的图像文件
    
    Args:
        filename: 文件名
        
    Returns:
        图像文件
    """
    file_path = Path(GENERATED_IMAGES_DIR) / filename
    
    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"图像文件不存在: {filename}"
        )
    
    # 检查文件扩展名
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型"
        )
    
    return FileResponse(
        path=str(file_path),
        media_type="image/png" if filename.lower().endswith('.png') else "image/jpeg",
        filename=filename
    )


@router.get("/images")
async def list_generated_images():
    """
    列出所有生成的图像文件
    
    Returns:
        图像文件列表
    """
    images_dir = Path(GENERATED_IMAGES_DIR)
    
    if not images_dir.exists():
        return {"images": [], "total_count": 0}
    
    image_files = []
    for file_path in images_dir.glob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            stat = file_path.stat()
            image_files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "created_at": stat.st_ctime,
                "modified_at": stat.st_mtime
            })
    
    # 按修改时间排序
    image_files.sort(key=lambda x: x["modified_at"], reverse=True)
    
    return {
        "images": image_files,
        "total_count": len(image_files)
    }


def setup_static_files(app):
    """
    设置静态文件服务
    
    Args:
        app: FastAPI应用实例
    """
    # 确保目录存在
    os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)
    
    # 挂载前端静态文件目录
    static_dir = Path(__file__).parent.parent.parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # 单独挂载生成图像目录
    app.mount("/generated", StaticFiles(directory=GENERATED_IMAGES_DIR), name="generated")
