# ModelScope 部署指令

## 📦 Step 1: 克隆 ModelScope 项目空间

```bash
git lfs install
git clone http://oauth2:ms-02dc2891-5f5e-416b-ad6b-57b8d9e61280@www.modelscope.cn/studios/Watchmen/Reelive-V2.1.git
cd Reelive-V2.1
```

## 🔧 Step 2: 配置环境变量（ModelScope Web UI）

**⚠️ 重要**: 在 ModelScope 控制台设置以下环境变量（**不要提交到 Git**）：

```bash
DASHSCOPE_API_KEY=sk-xxxxx         # 阿里云 DashScope
MODELSCOPE_API_KEY=ms-xxxxx        # ModelScope API
MINIMAX_API_KEY=mm-xxxxx           # MiniMax 图片生成
```

## 📂 Step 3: 复制编译文件到 Git 仓库

```bash
# 将本地 deploy125 文件夹的内容复制到克隆的仓库
# （根据你的操作系统选择命令）

# Windows PowerShell
Copy-Item -Path "E:\VScodeprojects\Reelive\deploy125\*" -Destination ".\Reelive-V2.1\" -Recurse -Force

# Linux/macOS
cp -r /path/to/Reelive/deploy125/* ./Reelive-V2.1/
```

## 📤 Step 4: 提交文件到 Git

```bash
cd Reelive-V2.1

# 查看待提交文件
git status

# 添加所有文件
git add .

# 提交
git commit -m "Deploy: ModelScope v2.1 - FastAPI + React production build"

# 推送到远程仓库
git push origin main
```

## 🚀 Step 5: ModelScope 自动构建

- ModelScope 检测到 `Dockerfile` 后会自动开始构建
- 等待容器启动（约 2-3 分钟）
- 构建日志可在 ModelScope 控制台查看

## ✅ Step 6: 验证部署

### 6.1 访问应用

```
https://www.modelscope.cn/studios/Watchmen/Reelive-V2.1
```

### 6.2 健康检查

```bash
curl https://www.modelscope.cn/studios/Watchmen/Reelive-V2.1/health

# 预期返回:
# {"status": "ok", "version": "2.0"}
```

### 6.3 测试 API

```bash
curl -X POST https://www.modelscope.cn/studios/Watchmen/Reelive-V2.1/api/aliyun/compatible-mode/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-max",
    "messages": [{"role": "user", "content": "测试"}]
  }'
```

## 📊 部署检查清单

- [x] ✅ 前端已构建 (393.47 kB JS bundle)
- [x] ✅ 后端代码已复制
- [x] ✅ Dockerfile 路径已修正
- [x] ✅ requirements.txt 已复制
- [x] ✅ README.md 已创建
- [x] ✅ .gitignore 已配置
- [ ] ⏳ 环境变量已在 ModelScope 控制台配置
- [ ] ⏳ 文件已推送到 Git 仓库
- [ ] ⏳ ModelScope 容器已启动
- [ ] ⏳ 健康检查通过

## 🛡️ 安全提醒

1. **不要提交 .env 文件** - 已在 .gitignore 中排除
2. **API Keys 仅在 ModelScope 控制台配置** - 不要硬编码
3. **验证 CORS 配置** - 如需外部调用，检查 ALLOWED_ORIGINS

## 🔄 回滚方案

如果部署失败：

```bash
# 在 ModelScope 控制台选择历史版本回滚
# 或临时修改环境变量启用调试模式
```

## 📚 相关文档

- [deploy125/README.md](../deploy125/README.md) - 部署版本说明
- [主项目 README](../README.md) - 开发环境指南
