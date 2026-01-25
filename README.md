# 叙事引擎 - ModelScope 部署版

**架构**: FastAPI (Python 3.12) + React 19 + Vite

## 📌 快速部署

### 1. 环境变量配置

在 ModelScope 控制台设置：

```bash
DASHSCOPE_API_KEY=sk-xxxxx       # 阿里云 DashScope
MODELSCOPE_API_KEY=ms-xxxxx      # ModelScope API
MINIMAX_API_KEY=mm-xxxxx          # MiniMax 图片生成
```

### 2. 自动构建

ModelScope 会自动识别 `Dockerfile` 并构建容器：
- **端口**: 7860
- **框架**: FastAPI (Uvicorn ASGI)
- **前端**: React 静态文件托管在 `/dist`

### 3. 访问应用

```
https://www.modelscope.cn/studios/Watchmen/Reelive-V2.1
```

## 📂 目录结构

```
deploy125/
├── backend/app/        # FastAPI 应用核心
├── dist/               # React 前端构建产物
├── Dockerfile          # 多阶段构建配置
└── requirements.txt    # Python 依赖
```

## 🔍 健康检查

```bash
curl https://your-app.modelscope.cn/health
# 预期: {"status": "ok", "version": "2.0"}
```

## ⚠️ 注意事项

1. **API Keys**: 必须在 ModelScope 环境变量中配置，不要提交到 Git
2. **音频文件**: `dist/audio/bgm/` 包含 20 个场景背景音乐（约 40MB）
3. **CORS**: 同源部署，无需额外配置

## 🛠️ 本地测试

```bash
# 构建镜像
docker build -t reelive:test .

# 运行容器（需要 .env 文件）
docker run -p 7860:7860 --env-file .env reelive:test

# 访问
open http://localhost:7860
```

## 📚 API 文档

FastAPI 自动文档：`https://your-app.modelscope.cn/docs`
