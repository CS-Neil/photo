## 摄影调色分析工具

输入大师参考图片，分析影调和色彩特征；再输入自己的照片，生成 Lightroom 调色参数预设。

### 快速开始

```bash
# 安装后端依赖
cd backend && pip install -r requirements.txt

# 安装前端依赖
cd frontend && npm install

# 一键启动（后端 :8000 + 前端 :3000）
./start.sh
```

浏览器打开 http://localhost:3000

### 功能

1. 上传大师参考图 → 生成直方图 + 影调/色彩分析文字
2. 上传自己照片 → 对比分析 → 输出 Lightroom 调色参数
3. 导出选项：复制文字参数 / 下载 XMP 预设文件

### 技术栈

- 前端: Next.js + TailwindCSS + Recharts
- 后端: Python FastAPI + OpenCV + NumPy + scikit-learn
- AI: Claude API (用户自备 Key)
