# 使用 Python 3.8 作为基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# 复制项目文件
COPY requirements.txt .
COPY main.py .
COPY nacos_middleware.py .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/ || exit 1

# 启动服务
CMD ["python", "main.py"] 