"""
Wan 文本到图像生成服务 - 使用阿里云 DashScope API
"""
import os
import asyncio
import time
from typing import Optional, Dict, Any
from pathlib import Path
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from dashscope import ImageSynthesis
import dashscope
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException

from ..config import config
from ..core.ids import generate_ulid
from ..core.lww import now_ms


# 配置 DashScope API
dashscope.base_http_api_url = config.WAN_API_BASE_URL


class WanImageGenerationService:
    """Wan 文本到图像生成服务"""
    
    def __init__(self):
        """初始化服务"""
        # 获取 API Key
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")
        
        # 输出目录
        self.output_dir = Path(config.WAN_IMAGE_OUTPUT_DIR)
        if not self.output_dir.is_absolute():
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.output_dir = Path(project_root) / self.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置参数
        self.model = config.WAN_IMAGE_MODEL
        self.size = config.WAN_IMAGE_SIZE
        self.prompt_extend = config.WAN_PROMPT_EXTEND
        self.watermark = config.WAN_WATERMARK
    
    async def generate_image_from_text(
        self,
        positive_prompt: str,
        negative_prompt: str = "",
        output_filename: Optional[str] = None,
        seed: Optional[int] = None,
        n: int = 1
    ) -> Dict[str, Any]:
        """
        从文本生成图像
        
        Args:
            positive_prompt: 正面提示词
            negative_prompt: 负面提示词
            output_filename: 输出文件名（不含扩展名），如果为None则自动生成
            seed: 随机种子
            n: 生成图像数量，默认1
            
        Returns:
            生成结果信息
        """
        start_time = time.time()
        
        # 生成输出文件名
        if output_filename is None:
            output_filename = f"wan_image_{generate_ulid()}"
        
        # 调用异步API
        print(f"正在调用 Wan API 生成图像...")
        print(f"提示词: {positive_prompt}")
        
        rsp = ImageSynthesis.async_call(
            api_key=self.api_key,
            model=self.model,
            prompt=positive_prompt,
            negative_prompt=negative_prompt if negative_prompt else "",
            n=n,
            size=self.size,
            prompt_extend=self.prompt_extend,
            watermark=self.watermark,
            seed=seed
        )
        
        if rsp.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f'Wan API调用失败: status_code={rsp.status_code}, '
                f'code={rsp.code}, message={rsp.message}'
            )
        
        task_id = rsp.output.task_id
        print(f"任务ID: {task_id}")
        
        # 等待任务完成（使用手动轮询，添加重试机制和错误处理）
        print("等待图像生成完成...")
        max_retries = 5
        retry_count = 0
        max_wait_time = 300  # 最大等待时间（秒）
        start_wait_time = time.time()
        last_status = None
        
        while True:
            try:
                # 检查是否超时
                elapsed_time = time.time() - start_wait_time
                if elapsed_time > max_wait_time:
                    raise RuntimeError(f"图像生成超时（超过 {max_wait_time} 秒），任务ID: {task_id}")
                
                # 使用 fetch 查询任务状态（传入 api_key）
                try:
                    status_rsp = ImageSynthesis.fetch(rsp, api_key=self.api_key)
                except Exception as fetch_error:
                    # fetch 调用本身失败，可能是网络问题
                    if retry_count < max_retries:
                        retry_count += 1
                        wait_time = min(10 * retry_count, 30)
                        print(f"查询任务状态时发生错误: {type(fetch_error).__name__}: {str(fetch_error)}")
                        print(f"{wait_time}秒后重试 {retry_count}/{max_retries}...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"查询任务状态失败，已重试 {max_retries} 次: {type(fetch_error).__name__}: {str(fetch_error)}")
                
                if status_rsp.status_code != HTTPStatus.OK:
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f"查询任务状态失败，重试 {retry_count}/{max_retries}...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        raise RuntimeError(
                            f'查询任务状态失败: status_code={status_rsp.status_code}, '
                            f'code={status_rsp.code}, message={status_rsp.message}'
                        )
                
                task_status = status_rsp.output.task_status
                last_status = task_status
                print(f"任务状态: {task_status} (已等待 {elapsed_time:.1f} 秒)")
                
                if task_status == "SUCCEEDED":
                    rsp = status_rsp
                    print(f"图像生成成功！总耗时: {elapsed_time:.1f} 秒")
                    break
                elif task_status == "FAILED":
                    error_msg = "未知错误"
                    if hasattr(status_rsp.output, 'message') and status_rsp.output.message:
                        error_msg = status_rsp.output.message
                    elif hasattr(status_rsp, 'message') and status_rsp.message:
                        error_msg = status_rsp.message
                    raise RuntimeError(f"图像生成失败: {error_msg}")
                elif task_status in ["PENDING", "RUNNING"]:
                    # 任务还在进行中，等待后继续查询
                    retry_count = 0
                    await asyncio.sleep(10)
                else:
                    # 未知状态，等待后重试
                    print(f"警告: 未知任务状态 '{task_status}'")
                    await asyncio.sleep(5)
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise RuntimeError(f"任务状态异常: {task_status}，已重试 {max_retries} 次")
                    
            except (ConnectionResetError, ConnectionError, RequestsConnectionError, Timeout, RequestException) as e:
                elapsed_time = time.time() - start_wait_time
                if retry_count < max_retries:
                    retry_count += 1
                    wait_time = min(10 * retry_count, 30)
                    print(f"网络连接错误 ({elapsed_time:.1f}秒)，{wait_time}秒后重试 {retry_count}/{max_retries}...")
                    print(f"错误详情: {type(e).__name__}: {str(e)}")
                    await asyncio.sleep(wait_time)
                    if not hasattr(rsp, 'output') or not hasattr(rsp.output, 'task_id'):
                        class TaskOutput:
                            def __init__(self, task_id):
                                self.task_id = task_id
                        class TaskResponse:
                            def __init__(self, task_id):
                                self.output = TaskOutput(task_id)
                        rsp = TaskResponse(task_id)
                else:
                    raise RuntimeError(f"网络连接失败，已重试 {max_retries} 次 (总耗时 {elapsed_time:.1f}秒): {type(e).__name__}: {str(e)}")
            except Exception as e:
                elapsed_time = time.time() - start_wait_time
                print(f"未知错误 ({elapsed_time:.1f}秒): {type(e).__name__}: {str(e)}")
                if retry_count < max_retries:
                    retry_count += 1
                    wait_time = min(10 * retry_count, 30)
                    print(f"{wait_time}秒后重试 {retry_count}/{max_retries}...")
                    await asyncio.sleep(wait_time)
                else:
                    raise RuntimeError(f"图像生成过程中发生错误 (总耗时 {elapsed_time:.1f}秒): {type(e).__name__}: {str(e)}")
        
        if rsp.status_code != HTTPStatus.OK:
            raise RuntimeError(
                f'图像生成失败: status_code={rsp.status_code}, '
                f'code={rsp.code}, message={rsp.message}'
            )
        
        # 下载图像
        image_paths = []
        image_urls = []
        
        for result in rsp.output.results:
            image_url = result.url
            print(f"图像URL: {image_url}")
            
            # 下载图像
            image_path = await self._download_image(image_url, output_filename, len(image_paths))
            image_paths.append(str(image_path))
            image_urls.append(f"/generated/{image_path.name}")
        
        image_generation_time = time.time() - start_time
        
        result = {
            "image_paths": image_paths,
            "image_urls": image_urls,
            "image_filename": image_paths[0] if image_paths else "",
            "image_url": image_urls[0] if image_urls else "",
            "image_size_mb": round(Path(image_paths[0]).stat().st_size / 1024 / 1024, 2) if image_paths else 0,
            "image_generation_seconds": round(image_generation_time, 2),
            "task_id": task_id
        }
        
        total_time = time.time() - start_time
        result["total_seconds"] = round(total_time, 2)
        
        return result
    
    async def _download_image(self, image_url: str, output_filename: str, index: int = 0) -> Path:
        """
        下载图像文件
        
        Args:
            image_url: 图像URL
            output_filename: 输出文件名（不含扩展名）
            index: 图像索引（如果生成多张图像）
            
        Returns:
            图像文件路径
        """
        # 从URL中提取文件名
        file_name = PurePosixPath(unquote(urlparse(image_url).path)).parts[-1]
        
        # 如果没有扩展名，使用默认扩展名
        if not file_name or '.' not in file_name:
            file_name = f"{output_filename}_{index}.png"
        elif index > 0:
            # 如果有多个图像，添加索引
            name, ext = file_name.rsplit('.', 1)
            file_name = f"{name}_{index}.{ext}"
        else:
            # 使用原始文件名，但确保前缀匹配
            name, ext = file_name.rsplit('.', 1)
            file_name = f"{output_filename}.{ext}"
        
        image_path = self.output_dir / file_name
        
        # 下载图像
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"图像已下载: {image_path}")
        return image_path


# 全局服务实例
_wan_image_service: Optional[WanImageGenerationService] = None


def get_wan_image_service() -> WanImageGenerationService:
    """获取Wan图像生成服务实例"""
    global _wan_image_service
    if _wan_image_service is None:
        _wan_image_service = WanImageGenerationService()
    return _wan_image_service

