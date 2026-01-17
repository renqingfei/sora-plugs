# -*- coding: utf-8 -*-
"""
数据模型定义
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class VideoSubmitRequest(BaseModel):
    """视频生成提交请求"""
    prompt: str = Field(..., description="视频描述文本")
    images: List[str] = Field(..., description="图片列表（支持本地路径或网络URL）")
    orientation: Optional[str] = Field(default="landscape", description="视频方向: portrait(竖屏) / landscape(横屏)")
    size: Optional[str] = Field(default="large", description="分辨率: large(1080p) / small(720p)")
    model: Optional[str] = Field(default="sora-2", description="模型名称")
    duration: Optional[int] = Field(default=8, description="视频时长(秒)，可选 4, 8, 12")
    watermark: Optional[bool] = Field(default=False, description="是否有水印，False=无水印，True=有水印")


class VideoSubmitResponse(BaseModel):
    """视频生成提交响应"""
    taskId: str = Field(..., description="任务ID")


class VideoTaskResponse(BaseModel):
    """视频任务查询响应"""
    taskId: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态: pending|processing|completed|failed")
    result: Optional[str] = Field(default=None, description="视频URL（completed时返回）")
    progress: Optional[float] = Field(default=None, description="进度百分比")
    failReason: Optional[str] = Field(default=None, description="失败原因")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    code: Optional[int] = Field(default=None, description="错误码")
