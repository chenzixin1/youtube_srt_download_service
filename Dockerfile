# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py ./

# 暴露端口
EXPOSE 5000

# 启动服务
CMD ["python", "app.py"] 