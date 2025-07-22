# YouTube SRT Download Service

本项目用于下载 YouTube 视频的字幕（SRT 文件）。

## 主要功能
- 输入 YouTube 视频链接，自动下载对应的字幕（SRT 格式）。
- 支持多种语言字幕下载（如视频提供）。

## 安装方法
1. 克隆仓库：
   ```bash
   git clone https://github.com/你的用户名/你的仓库名.git
   cd youtube_srt_download_service
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 运行方法
```bash
python app.py
```

## Docker 部署
如需使用 Docker 部署：
```bash
docker build -t youtube-srt-download .
docker run -p 8000:8000 youtube-srt-download
```

## 贡献
欢迎提交 issue 和 PR！ 