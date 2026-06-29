# 摄影调色分析 Web 应用 — 实现计划

## 架构概览

```
┌─────────────────────────────────────┐
│         Next.js Frontend            │
│  (React + TailwindCSS + shadcn/ui) │
├─────────────────────────────────────┤
│  上传参考图 → 查看分析结果           │
│  上传自己照片 → 获取 LR 参数        │
│  选择输出格式 (文字 / XMP 下载)     │
└──────────────┬──────────────────────┘
               │ HTTP API
┌──────────────▼──────────────────────┐
│        Python FastAPI Backend        │
├──────────────────────────────────────┤
│  /api/analyze    分析参考图          │
│  /api/match      对比+生成LR参数     │
├──────────────────────────────────────┤
│  OpenCV + NumPy   图像分析引擎       │
│  Claude API       文字描述+参数建议  │
│  XMP 模板引擎    生成预设文件        │
└──────────────────────────────────────┘
```

## 目录结构

```
media/
├── frontend/                  # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # 主页面
│   │   │   ├── layout.tsx     # 布局
│   │   │   └── globals.css    # 全局样式
│   │   ├── components/
│   │   │   ├── ImageUploader.tsx    # 图片上传组件
│   │   │   ├── HistogramChart.tsx   # 直方图展示
│   │   │   ├── AnalysisResult.tsx   # 分析结果展示
│   │   │   ├── LRParams.tsx         # LR 参数展示
│   │   │   └── ApiKeyInput.tsx      # API Key 输入
│   │   └── lib/
│   │       └── api.ts               # 后端 API 调用封装
│   ├── package.json
│   ├── tailwind.config.ts
│   └── next.config.ts
├── backend/                   # Python FastAPI 后端
│   ├── main.py                # FastAPI 入口
│   ├── analyzer/
│   │   ├── histogram.py       # 直方图计算
│   │   ├── tone.py            # 影调分析
│   │   ├── color.py           # 色彩分析
│   │   └── matcher.py         # 参数匹配引擎
│   ├── llm/
│   │   └── claude.py          # Claude API 调用
│   ├── export/
│   │   ├── xmp.py             # XMP 预设生成
│   │   └── template.xmp       # XMP 模板文件
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## 实现步骤

### Phase 1: 后端 — 图像分析引擎

**Step 1.1: 项目初始化**
- 创建 FastAPI 项目，配置 CORS
- 安装依赖: fastapi, uvicorn, opencv-python-headless, numpy, pillow, httpx

**Step 1.2: 直方图分析 (`analyzer/histogram.py`)**
- RGB 三通道直方图数据
- 亮度 (Luminance) 直方图
- 返回 256 bin 的数组，供前端绘图

**Step 1.3: 影调分析 (`analyzer/tone.py`)**
- 计算: 平均亮度、标准差(对比度)、偏度(高/低调倾向)
- 分区统计: 阴影(0-85)、中间调(86-170)、高光(171-255) 占比
- 判定: 高调/低调/中间调、高对比/低对比
- 动态范围估算

**Step 1.4: 色彩分析 (`analyzer/color.py`)**
- 转 HSV 空间，统计色相分布
- 色温估算 (基于 R/B 比值 + 平均色相)
- 整体饱和度水平
- 分区色彩偏移: 阴影区/中间调/高光区各自的色相偏向
- 主色调提取 (K-means 聚类取 Top 5 色)

**Step 1.5: 参数匹配引擎 (`analyzer/matcher.py`)**
- 输入: 参考图分析数据 + 用户照片分析数据
- 计算差异: 曝光差、对比度差、色温差、各区间亮度差、饱和度差
- 映射为 Lightroom 参数:
  - 基础: Exposure, Contrast, Highlights, Shadows, Whites, Blacks
  - 色温: Temperature, Tint
  - 色调曲线: ToneCurvePV2012 (四点控制)
  - HSL: HueAdjustment, SaturationAdjustment, LuminanceAdjustment
  - 色调分离: SplitToningShadowHue/Saturation, HighlightHue/Saturation
  - 色彩校准: ShadowTint, RedHueCalibration 等

### Phase 2: 后端 — LLM 集成 & 导出

**Step 2.1: Claude API 集成 (`llm/claude.py`)**
- 接收用户提供的 API Key
- 将图像分析的数值数据 + 直方图特征作为上下文
- Prompt 设计:
  - 分析阶段: 请用摄影术语描述这张照片的影调和色彩特点
  - 匹配阶段: 基于数值差异，给出调色思路说明

**Step 2.2: XMP 导出 (`export/xmp.py`)**
- 标准 Adobe XMP 模板
- 填充计算得到的 LR 参数
- 生成合规的 .xmp 文件供下载导入 Lightroom

**Step 2.3: API 路由整合 (`main.py`)**
- `POST /api/analyze` — 上传参考图，返回直方图数据 + 影调色彩分析文字
- `POST /api/match` — 上传用户照片 + 参考图分析结果，返回 LR 参数
- `GET /api/export/xmp` — 下载 XMP 预设文件

### Phase 3: 前端 — Web 界面

**Step 3.1: Next.js 项目初始化**
- create-next-app + TailwindCSS + shadcn/ui
- 配置代理到 FastAPI 后端

**Step 3.2: 主页面流程 UI**
- 步骤 1: 输入 API Key (存 localStorage)
- 步骤 2: 上传参考图 → 显示直方图 + 分析结果
- 步骤 3: 上传自己照片 → 显示对比 + LR 参数
- 步骤 4: 选择导出方式 (文字复制 / XMP 下载)

**Step 3.3: 直方图组件**
- 用 Canvas 或 recharts 绘制 RGB + 亮度直方图
- 参考图和用户照片的直方图并排对比

**Step 3.4: 分析结果展示**
- 影调分析卡片 (数值 + 文字描述)
- 色彩分析卡片 (色轮可视化 + 主色调色板 + 文字描述)
- LR 参数面板 (分组展示，可折叠)

### Phase 4: 集成联调

- 前后端联调
- 错误处理 (图片过大、格式不支持、API Key 无效)
- 加载状态和进度反馈

## 关键技术决策

1. **图像传输**: 前端将图片 base64 编码后 POST 到后端，限制最大 20MB
2. **LR 参数映射**: 使用线性/非线性映射 + 经验系数，核心逻辑在 matcher.py
3. **Claude 的角色**: 不做参数计算（不够精确），而是对算法计算的结果做文字润色和调色思路说明
4. **XMP 兼容性**: 基于 Adobe Camera Raw 15.x 的 XMP namespace，兼容 LR Classic / LR CC
