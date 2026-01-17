# -*- coding: utf-8 -*-
"""
图床上传模块
使用 litterbox.catbox.moe 临时图床（72小时）
"""
import httpx
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

# litterbox 上传地址
LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"


async def upload_to_litterbox(file_path: str) -> str:
    """
    上传图片到 litterbox（72小时临时图床）

    Args:
        file_path: 本地图片文件路径

    Returns:
        图片的网络URL
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(path, "rb") as f:
        file_data = f.read()

    filename = path.name
    content_type = _get_content_type(path.suffix.lower())

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        files = {"fileToUpload": (filename, file_data, content_type)}
        data = {"reqtype": "fileupload", "time": "72h"}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        response = await client.post(
            LITTERBOX_URL,
            files=files,
            data=data,
            headers=headers
        )
        response.raise_for_status()

        url = response.text.strip()
        if not url.startswith("http"):
            raise Exception(f"上传失败: {url}")

        logger.info(f"图片上传成功: {url}")
        return url


def _get_content_type(suffix: str) -> str:
    """根据文件后缀获取MIME类型"""
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    return content_types.get(suffix, "application/octet-stream")


def is_local_path(path: str) -> bool:
    """判断是否为本地文件路径"""
    if path.startswith("http://") or path.startswith("https://"):
        return False
    return True


async def process_images(images: List[str]) -> List[str]:
    """
    处理图片列表，将本地路径上传到图床

    Args:
        images: 图片列表（可能是本地路径或URL）

    Returns:
        全部为网络URL的图片列表
    """
    result = []
    for image in images:
        if is_local_path(image):
            # 本地路径，上传到图床
            url = await upload_to_litterbox(image)
            result.append(url)
        else:
            # 已经是URL，直接使用
            result.append(image)
    return result
