# Sora-2 视频生成插件

基于云雾API的Sora-2视频生成插件，支持异步模式的图生视频功能。

## 功能特性

- 支持图生视频（需提供参考图片）
- 异步任务模式，支持任务状态查询
- 支持多种视频比例：1:1、16:9、9:16
- 支持多种分辨率：720p、1080p
- 支持自定义视频时长：5/10/15/20秒
- 支持 sora-2 和 sora-2-pro 模型

## 目录结构

```
sora2-plugin/
├── main.py           # 主程序入口
├── config.py         # 配置文件
├── models.py         # 数据模型
├── yunwu_client.py   # 云雾API客户端
├── plugins.json      # 插件配置
├── requirements.txt  # Python依赖
├── start.bat         # Windows启动脚本
└── README.md         # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# Windows 双击运行
start.bat

# 或命令行启动
python main.py
```

服务将在 `http://127.0.0.1:13005` 启动。

## API接口

### 提交视频任务

```
POST /v1/videos/submit
```

**请求头：**
| 参数 | 说明 |
|------|------|
| Content-Type | application/json |
| sessionId | 云雾API Token |

**请求体：**
```json
{
  "prompt": "视频描述文本",
  "images": ["https://example.com/image.jpg"],
  "ratio": "16:9",
  "resolution": "1080p",
  "model": "sora-2",
  "duration": 5,
  "watermark": false
}
```

**响应：**
```json
{
  "taskId": "sora-2:task_xxxxx"
}
```

### 查询任务状态

```
GET /v1/videos/tasks/{taskId}
```

**请求头：**
| 参数 | 说明 |
|------|------|
| sessionId | 云雾API Token |

**响应：**
```json
{
  "taskId": "sora-2:task_xxxxx",
  "status": "completed",
  "result": "https://example.com/video.mp4",
  "progress": 1.0,
  "failReason": null
}
```

**状态说明：**
- `pending`: 等待处理
- `processing`: 处理中
- `completed`: 已完成
- `failed`: 失败

## 插件配置

将 `plugins.json` 中的配置添加到主程序的插件配置中即可使用。

## 注意事项

1. 使用前需要先获取云雾API的Token
2. 图生视频模式必须提供至少一张参考图片
3. 视频生成是异步过程，需要轮询查询任务状态
