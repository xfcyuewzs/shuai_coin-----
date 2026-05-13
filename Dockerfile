# 使用官方 Python 3.12 镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (psycopg2 需要)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令 (使用 gunicorn，4 个工作进程)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "run:app"]
