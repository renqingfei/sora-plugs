# 插件开发规范

## 一、插件接口规范

插件需要实现以下 HTTP 接口：

### 文生图

```
POST /v1/images/generations
```

### 图生图

```
POST /v1/images/compositions
```

### 视频生成（同步模式）

```
POST /v1/videos/generations
```

### 视频生成（异步模式）

当插件配置 `isSync: false` 时，需要实现以下接口：

**提交任务：**
```
POST /v1/videos/submit
```
返回：
```json
{
  "taskId": "任务ID"
}
```

**查询任务：**
```
GET /v1/videos/tasks/{taskId}
```
返回：
```json
{
  "taskId": "任务ID",
  "status": "pending|processing|completed|failed",
  "result": "视频URL（completed 时返回）"
}
```

---

## 二、请求格式

### 请求头

| 参数 | 说明 |
|------|------|
| Content-Type | application/json |
| sessionId | 用户认证 Token |

### 请求体

```json
{
  "prompt": "描述文本",
  "ratio": "1:1",
  "resolution": "2k",
  "model": "jimeng-4.0",
  "sample_strength": 0.7,
  "images": ["url1", "url2"]
}
```

> `images` 仅视频生成接口使用

---

## 三、插件配置 (plugins.json)

### 文件结构

```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-01-01",
  "baseUrl": "https://your-download-url/",
  "plugins": []
}
```

### 插件定义

```json
{
  "id": "my-plugin",
  "version": "1.0.0",
  "name": "插件名称",
  "type": "image,video",
  "host": "http://127.0.0.1",
  "port": 13002,
  "exe": "my-plugin.exe",
  "description": "插件描述",
  "fileName": "my-plugin-1.0.0.zip",
  "params": [],
  "options": []
}
```

| 字段 | 说明 |
|------|------|
| id | 插件唯一标识 |
| version | 版本号 |
| name | 显示名称 |
| type | 支持类型：`image` / `video` / `image,video` |
| host | 服务地址 |
| port | 服务端口 |
| exe | 可执行文件名 |
| fileName | 下载包文件名 |
| isSync | 是否同步模式：`true` 同步 / `false` 异步（仅视频） |
| options | 配置选项列表 |

---

## 四、配置选项 (options)

### 选项结构

```json
{
  "key": "参数名",
  "label": "显示标签",
  "type": "select",
  "required": true,
  "hidden": false,
  "isHeader": false,
  "default": "默认值",
  "placeholder": "提示文本",
  "scope": "image,video",
  "options": [
    { "label": "显示文本", "value": "实际值" }
  ]
}
```

| 字段 | 说明 |
|------|------|
| key | 参数名（对应请求体字段） |
| label | 界面显示标签 |
| type | 类型：`select` / `input` / `number` / `password` |
| required | 是否必填 |
| hidden | 是否隐藏（内部参数设为 true） |
| isHeader | true 时作为请求头传递，false 时放入请求体 |
| lineShow | 是否在行内展示 |
| default | 默认值 |
| scope | 作用范围：`image` / `video` / `image,video` |
| options | 下拉选项（type=select 时使用） |

---

## 五、完整配置示例

```json
{
  "version": "1.0.0",
  "lastUpdated": "2025-01-01",
  "baseUrl": "https://github.com/xxx/releases/latest/download/",
  "plugins": [
    {
      "id": "my-plugin",
      "version": "1.0.0",
      "name": "我的插件",
      "type": "image,video",
      "host": "http://127.0.0.1",
      "port": 13002,
      "exe": "my-plugin.exe",
      "description": "AI 图片和视频生成",
      "fileName": "my-plugin-1.0.0.zip",
      "params": [],
      "options": [
        {
          "key": "sessionId",
          "label": "会话ID",
          "type": "password",
          "required": true,
          "hidden": false,
          "isHeader": true,
          "default": "",
          "placeholder": "请输入会话ID",
          "scope": "image,video"
        },
        {
          "key": "ratio",
          "label": "比例",
          "type": "select",
          "required": true,
          "hidden": false,
          "isHeader": false,
          "default": "1:1",
          "scope": "image,video",
          "options": [
            { "label": "1:1", "value": "1:1" },
            { "label": "16:9", "value": "16:9" },
            { "label": "9:16", "value": "9:16" }
          ]
        },
        {
          "key": "resolution",
          "label": "分辨率",
          "type": "select",
          "required": true,
          "hidden": false,
          "isHeader": false,
          "default": "2k",
          "scope": "image",
          "options": [
            { "label": "1k", "value": "1k" },
            { "label": "2k", "value": "2k" },
            { "label": "4k", "value": "4k" }
          ]
        },
        {
          "key": "resolution",
          "label": "分辨率",
          "type": "select",
          "required": true,
          "hidden": false,
          "isHeader": false,
          "default": "720p",
          "scope": "video",
          "options": [
            { "label": "720p", "value": "720p" },
            { "label": "1080p", "value": "1080p" }
          ]
        },
        {
          "key": "model",
          "label": "模型",
          "type": "select",
          "required": true,
          "hidden": false,
          "isHeader": false,
          "default": "model-v1",
          "scope": "image",
          "options": [
            { "label": "V1", "value": "model-v1" },
            { "label": "V2", "value": "model-v2" }
          ]
        }
      ]
    }
  ]
}
```

---

## 六、请求示例

**图片生成：**
```bash
curl -X POST http://127.0.0.1:13002/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "sessionId: your_token" \
  -d '{"prompt": "一只猫", "ratio": "1:1", "resolution": "2k", "model": "model-v1"}'
```

**视频生成：**
```bash
curl -X POST http://127.0.0.1:13002/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "sessionId: your_token" \
  -d '{"prompt": "猫在跑", "images": ["https://xxx.jpg"], "ratio": "16:9", "resolution": "1080p"}'
```
