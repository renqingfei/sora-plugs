# -*- coding: utf-8 -*-
"""
Sora-2 视频生成插件 - 异步模式
支持图生视频功能
"""
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from config import PLUGIN_HOST, PLUGIN_PORT
from models import (
    VideoSubmitRequest,
    VideoSubmitResponse,
    VideoTaskResponse,
    ErrorResponse
)
from yunwu_client import YunwuClient

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"Sora-2 插件启动，监听端口: {PLUGIN_PORT}")
    yield
    logger.info("Sora-2 插件关闭")


app = FastAPI(
    title="Sora-2 视频生成插件",
    description="基于云雾API的Sora-2视频生成插件，支持异步模式",
    version="1.0.0",
    lifespan=lifespan
)


@app.post(
    "/v1/videos/submit",
    response_model=VideoSubmitResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="提交视频生成任务",
    description="提交图生视频任务，返回任务ID用于后续查询"
)
async def submit_video(
    request: VideoSubmitRequest,
    sessionId: Optional[str] = Header(default=None, description="用户认证Token")
):
    """
    提交视频生成任务（异步模式）

    - **prompt**: 视频描述文本（必填）
    - **images**: 图片URL列表（必填）
    - **orientation**: 视频方向 portrait(竖屏) / landscape(横屏)
    - **size**: 分辨率 large(1080p) / small(720p)
    - **model**: 模型名称，默认 sora-2
    - **duration**: 视频时长（秒），可选 4, 8, 12
    - **watermark**: 是否有水印，false=无水印，true=有水印
    """
    if not sessionId:
        raise HTTPException(status_code=400, detail="缺少sessionId请求头")

    if not request.images or len(request.images) == 0:
        raise HTTPException(status_code=400, detail="图生视频模式必须提供images参数")

    try:
        client = YunwuClient(sessionId)
        result = await client.create_video(
            prompt=request.prompt,
            images=request.images,
            orientation=request.orientation,
            size=request.size,
            model=request.model,
            duration=request.duration,
            watermark=request.watermark
        )

        task_id = result.get("id")
        if not task_id:
            raise HTTPException(status_code=500, detail="创建任务失败：未返回任务ID")

        logger.info(f"任务创建成功: {task_id}")
        return VideoSubmitResponse(taskId=task_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建视频任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建视频任务失败: {str(e)}")


@app.get(
    "/v1/videos/tasks/{taskId}",
    response_model=VideoTaskResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="查询任务状态",
    description="根据任务ID查询视频生成任务的状态和结果"
)
async def query_task(
    taskId: str,
    sessionId: Optional[str] = Header(default=None, description="用户认证Token")
):
    """
    查询视频生成任务状态

    - **taskId**: 任务ID（路径参数）

    返回状态说明：
    - pending: 等待处理
    - processing: 处理中
    - completed: 已完成，result字段包含视频URL
    - failed: 失败，failReason字段包含失败原因
    """
    if not sessionId:
        raise HTTPException(status_code=400, detail="缺少sessionId请求头")

    try:
        client = YunwuClient(sessionId)
        result = await client.query_task(taskId)

        # 解析云雾API返回的状态
        detail = result.get("detail", {})
        pending_info = detail.get("pending_info", {})

        # 优先从 pending_info 获取实际状态，其次从 detail，最后从顶层
        status = pending_info.get("status") or detail.get("status") or result.get("status", "pending")

        # 获取进度
        progress = pending_info.get("progress_pct")

        # 获取视频URL和失败原因
        video_url = None
        fail_reason = None

        if status in ["completed", "succeed"]:
            # 优先从顶层 video_url 获取
            video_url = result.get("video_url")
            # 其次从 detail 获取
            if not video_url:
                video_url = detail.get("video_url")
            # 再从 generations 获取
            if not video_url:
                generations = pending_info.get("generations", [])
                if generations and len(generations) > 0:
                    video_url = generations[0].get("url") or generations[0].get("video_url")
            # 最后尝试 result 字段
            if not video_url:
                video_url = result.get("result") or detail.get("result")

        elif status == "failed":
            fail_reason = pending_info.get("failure_reason") or result.get("failure_reason") or "未知错误"

        # 状态映射
        status_map = {
            "pending": "pending",
            "processing": "processing",
            "completed": "completed",
            "failed": "failed",
            "succeed": "completed"
        }
        mapped_status = status_map.get(status, status)

        logger.info(f"查询任务 {taskId}: status={mapped_status}, progress={progress}")

        return VideoTaskResponse(
            taskId=taskId,
            status=mapped_status,
            result=video_url,
            progress=progress,
            failReason=fail_reason
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询任务失败: {str(e)}")


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "sora2-plugin"}


if __name__ == "__main__":
    uvicorn.run(
        app,  # 直接传递 app 对象，适配 PyInstaller 打包
        host=PLUGIN_HOST,
        port=PLUGIN_PORT,
        reload=False,
        log_level="info"
    )
