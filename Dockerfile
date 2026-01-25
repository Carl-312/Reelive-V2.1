# ============================================
# Stage 1: Builder - 构建环境
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /app

# 创建虚拟环境
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - 运行环境
# ============================================
FROM python:3.12-slim

WORKDIR /home/user/app

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH"

# 从构建阶段复制虚拟环境
COPY --from=builder /app/venv /app/venv

# 复制应用代码
COPY backend/app ./app

# 复制前端构建产物（必须先执行 cd frontend && npm run build）
COPY dist ./dist

# 暴露端口
EXPOSE 7860

# 启动命令 - 使用 Uvicorn ASGI 服务器
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
