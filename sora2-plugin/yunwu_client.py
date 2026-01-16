# -*- coding: utf-8 -*-
"""
云雾API客户端
"""
import httpx
from typing import Optional, List, Dict, Any

from config import YUNWU_CREATE_VIDEO_URL, YUNWU_QUERY_TASK_URL, DEFAULT_MODEL


class YunwuClient:
    """云雾API客户端"""

    def __init__(self, session_id: str):
        """
        初始化客户端

        Args:
            session_id: 用户认证Token
        """
        self.session_id = session_id
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {session_id}"
        }

    async def create_video(
        self,
        prompt: str,
        images: List[str],
        orientation: str = "landscape",
        size: str = "large",
        model: str = DEFAULT_MODEL,
        duration: int = 8,
        watermark: bool = False
    ) -> Dict[str, Any]:
        """
        创建视频任务

        Args:
            prompt: 视频描述
            images: 图片URL列表
            orientation: 视频方向 portrait(竖屏) / landscape(横屏)
            size: 分辨率 large(1080p) / small(720p)
            model: 模型名称
            duration: 视频时长(秒)，可选 4, 8, 12
            watermark: 是否有水印，False=无水印，True=有水印

        Returns:
            API响应数据
        """
        # 确保orientation值有效
        if orientation not in ["portrait", "landscape"]:
            orientation = "landscape"

        # 确保size值有效
        if size not in ["large", "small"]:
            size = "large"

        payload = {
            "prompt": prompt,
            "images": images,
            "model": model,
            "orientation": orientation,
            "size": size,
            "duration": duration,
            "watermark": watermark
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                YUNWU_CREATE_VIDEO_URL,
                headers=self.headers,
                json=payload
            )
            result = response.json()
            # 检查API返回的错误
            if result.get("status") == "error" or result.get("error"):
                error_msg = result.get("error") or result.get("message") or "未知错误"
                raise Exception(f"云雾API错误: {error_msg}")
            if response.status_code >= 400:
                response.raise_for_status()
            return result

    async def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            任务状态数据
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                YUNWU_QUERY_TASK_URL,
                headers=self.headers,
                params={"id": task_id}
            )
            response.raise_for_status()
            return response.json()
