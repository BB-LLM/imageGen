"""
Pydantic数据模型
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SoulBase(BaseModel):
    """Soul基础模型"""
    soul_id: str = Field(..., description="Soul ID，如nova、valentina")
    display_name: str = Field(..., description="显示名称")
    updated_at_ts: int = Field(..., description="更新时间戳")


class SoulStyleProfileBase(BaseModel):
    """Soul风格配置基础模型"""
    soul_id: str = Field(..., description="Soul ID")
    base_model_ref: str = Field(..., description="基础模型引用")
    lora_ids_json: List[str] = Field(..., description="LoRA ID列表")
    palette_json: Dict[str, Any] = Field(..., description="调色板配置")
    negatives_json: List[str] = Field(..., description="负面提示词")
    motion_module: Optional[str] = Field(None, description="动画模块")
    extra_json: Dict[str, Any] = Field(default_factory=dict, description="额外配置")
    updated_at_ts: int = Field(..., description="更新时间戳")


class PromptKeyBase(BaseModel):
    """提示词键基础模型"""
    pk_id: str = Field(..., description="提示词键ID")
    soul_id: str = Field(..., description="Soul ID")
    key_norm: str = Field(..., description="标准化提示词")
    key_hash: str = Field(..., description="提示词哈希")
    key_embed: Optional[bytes] = Field(None, description="嵌入向量")
    meta_json: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    updated_at_ts: int = Field(..., description="更新时间戳")


class VariantBase(BaseModel):
    """变体基础模型"""
    variant_id: str = Field(..., description="变体ID")
    pk_id: str = Field(..., description="提示词键ID")
    soul_id: str = Field(..., description="Soul ID")
    asset_url: str = Field(..., description="资源URL")
    storage_key: str = Field(..., description="存储键")
    seed: Optional[int] = Field(None, description="随机种子")
    phash: Optional[int] = Field(None, description="感知哈希")
    meta_json: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    updated_at_ts: int = Field(..., description="更新时间戳")


class UserSeenBase(BaseModel):
    """用户已看记录基础模型"""
    user_id: str = Field(..., description="用户ID")
    variant_id: str = Field(..., description="变体ID")
    seen_at_ts: int = Field(..., description="查看时间戳")


class LandmarkLogBase(BaseModel):
    """地标日志基础模型"""
    soul_id: str = Field(..., description="Soul ID")
    city_key: str = Field(..., description="城市键")
    landmark_key: str = Field(..., description="地标键")
    user_id: Optional[str] = Field(None, description="用户ID")
    used_at_ts: int = Field(..., description="使用时间戳")


class WorkLockBase(BaseModel):
    """工作锁基础模型"""
    lock_key: str = Field(..., description="锁键")
    owner_id: str = Field(..., description="拥有者ID")
    expires_at_ts: int = Field(..., description="过期时间戳")
    updated_at_ts: int = Field(..., description="更新时间戳")


class IdempotencyBase(BaseModel):
    """幂等性基础模型"""
    idem_key: str = Field(..., description="幂等性键")
    result_json: Dict[str, Any] = Field(..., description="结果JSON")
    updated_at_ts: int = Field(..., description="更新时间戳")


# API请求/响应模型
class ImageRequest(BaseModel):
    """图像生成请求"""
    soul_id: str = Field(..., description="Soul ID")
    cue: str = Field(..., description="提示词")
    user_id: str = Field(..., description="用户ID")


class ImageResponse(BaseModel):
    """图像生成响应"""
    url: str = Field(..., description="图像URL")
    variant_id: str = Field(..., description="变体ID")
    pk_id: str = Field(..., description="提示词键ID")


class SelfieRequest(BaseModel):
    """自拍请求"""
    soul_id: str = Field(..., description="Soul ID")
    city_key: str = Field(..., description="城市键")
    mood: str = Field(..., description="情绪")
    user_id: str = Field(..., description="用户ID")


class SelfieResponse(BaseModel):
    """自拍响应"""
    url: str = Field(..., description="图像URL")
    variant_id: str = Field(..., description="变体ID")
    pk_id: str = Field(..., description="提示词键ID")
    landmark_key: str = Field(..., description="地标键")


class StyleRequest(BaseModel):
    """风格配置请求"""
    soul_id: str = Field(..., description="Soul ID")
    base_model_ref: str = Field(..., description="基础模型引用")
    lora_ids: List[str] = Field(..., description="LoRA ID列表")
    palette: Dict[str, Any] = Field(..., description="调色板")
    negatives: List[str] = Field(..., description="负面提示词")
    motion_module: Optional[str] = Field(None, description="动画模块")


class ReferenceRequest(BaseModel):
    """参考图像请求"""
    soul_id: str = Field(..., description="Soul ID")
    url: str = Field(..., description="参考图像URL")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="状态")
    timestamp: int = Field(..., description="时间戳")
    database: str = Field(..., description="数据库状态")
    storage: str = Field(..., description="存储状态")
