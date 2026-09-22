# 新浪财经历史分红数据获取与预处理 — 需求确认计划（Plan）

> 文档版本：v1.0  
> 创建日期：2026-09-22  
> 项目目录：`C:\Users\Administrator\Desktop\123`

---

## 一、任务目标

完成新浪财经历史分红数据的获取、清洗、预处理，并通过网页可视化展示整个实现过程与最终结果。同时使用 Playwright 对网页进行自动化测试，确保交付质量。

## 二、考核点对照

| 序号 | 考核点 | 对应交付物 | 状态 |
|------|--------|-----------|------|
| 1 | Plan 模式确认需求 | 本文档 `plan.md` | ✅ 已确认 |
| 2 | UI/UX 专业设计 | `web/` 目录下的网页，含响应式布局、数据可视化 | ⏳ 待开发 |
| 3 | Playwright 网页测试 | `tests/playwright/` 测试脚本 + 测试报告 | ⏳ 待开发 |

## 三、交付物清单

### 3.1 必须交付

| 编号 | 交付物 | 格式 | 路径/位置 |
|------|--------|------|----------|
| D1 | Git 仓库链接 | URL | 远程仓库（GitHub/Gitee） |
| D2 | 展示网页 | HTML/CSS/JS | `web/index.html` |
| D3 | 网页截图 | PNG | `screenshots/` |
| D4 | 对话记录文档 | Markdown（脱敏） | `docs/conversation.md` |
| D5 | 数据获取脚本 | Python | `src/fetch_dividend.py` |
| D6 | 数据预处理脚本 | Python | `src/preprocess.py` |
| D7 | 原始数据 | CSV/JSON | `data/raw/` |
| D8 | 预处理后数据 | CSV/JSON | `data/processed/` |
| D9 | Playwright 测试脚本 | JS/TS | `tests/playwright/` |
| D10 | README 项目说明 | Markdown | `README.md` |

### 3.2 网页展示内容要求

网页必须包含以下板块：
1. **项目概述** — 任务背景、数据源说明
2. **数据获取过程** — 目标 URL、请求方式、字段说明、代码片段
3. **数据预处理过程** — 清洗规则、缺失值处理、格式转换、代码片段
4. **数据可视化结果** — 分红趋势图、分红金额分布、统计摘要
5. **技术栈说明** — Python / Playwright / ECharts 等

## 四、技术方案

### 4.1 数据获取

- **数据源**：新浪财经个股分红配股页面
  - 示例 URL：`https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{股票代码}.phtml`
- **选取股票**：选取 3-5 只代表性 A 股（如贵州茅台 600519、工商银行 601398、中国平安 601318 等），获取其历史分红数据
- **技术手段**：Python `requests` + `BeautifulSoup` / `lxml` 解析 HTML 表格
- **输出**：`data/raw/dividend_raw.csv`

### 4.2 数据预处理

- **清洗步骤**：
  1. 去除 HTML 标签残留与空白字符
  2. 统一日期格式（YYYY-MM-DD）
  3. 数值字段类型转换（分红金额、配股比例等）
  4. 缺失值标记与处理
  5. 按股票代码、年份分组聚合
- **输出**：`data/processed/dividend_clean.csv` + `data/processed/dividend_summary.json`

### 4.3 网页开发

- **技术栈**：原生 HTML5 + CSS3 + JavaScript（ES6+）
- **可视化库**：ECharts（CDN 引入）
- **UI/UX 设计原则**：
  - 现代简洁风格，卡片式布局
  - 响应式设计，适配桌面与移动端
  - 清晰的视觉层次与配色方案（避免大面积靛蓝/紫色）
  - 数据可视化图表交互（悬停提示、缩放）
  - 平滑滚动与过渡动画
- **页面结构**：单页应用（SPA），分板块锚点导航

### 4.4 Playwright 测试

- **测试框架**：Playwright（Node.js）
- **测试用例**：
  1. 页面加载测试 — 验证页面标题、关键元素存在
  2. 导航测试 — 验证锚点导航跳转
  3. 图表渲染测试 — 验证 ECharts 画布已渲染
  4. 数据展示测试 — 验证统计数据正确显示
  5. 响应式测试 — 验证不同视口下布局正常
- **输出**：测试报告 + 测试截图

## 五、项目目录结构

```
123/
├── plan.md                    # 本文件：需求确认计划
├── README.md                  # 项目说明文档
├── data/
│   ├── raw/                   # 原始爬取数据
│   └── processed/             # 预处理后数据
├── src/
│   ├── fetch_dividend.py      # 数据获取脚本
│   └── preprocess.py          # 数据预处理脚本
├── web/
│   ├── index.html             # 主页面
│   ├── css/
│   │   └── style.css          # 样式文件
│   └── js/
│       └── app.js             # 交互与可视化脚本
├── tests/
│   └── playwright/
│       ├── package.json       # Playwright 依赖
│       └── test.spec.js       # 测试用例
├── docs/
│   └── conversation.md        # 对话记录（脱敏）
└── screenshots/               # 网页截图
```

## 六、执行计划与时间线

| 阶段 | 任务 | 预计产出 |
|------|------|---------|
| Phase 1 | 环境确认 + 项目初始化 + Plan 文档 | 目录结构、plan.md |
| Phase 2 | 数据获取脚本开发与执行 | fetch_dividend.py、raw 数据 |
| Phase 3 | 数据预处理脚本开发与执行 | preprocess.py、clean 数据、summary |
| Phase 4 | 网页 UI/UX 设计与开发 | index.html、style.css、app.js |
| Phase 5 | Playwright 测试脚本开发与执行 | test.spec.js、测试报告 |
| Phase 6 | 网页截图采集 | screenshots/*.png |
| Phase 7 | 对话记录文档整理（脱敏） | docs/conversation.md |
| Phase 8 | Git 提交 + 远程仓库推送 | Git 链接 |
| Phase 9 | 最终整合与交付检查 | 全部交付物确认 |

## 七、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 新浪财经页面结构变更 | 数据爬取失败 | 增加异常处理，备选多只股票；如页面不可用则使用静态模拟数据并注明 |
| 网络请求被限制 | 数据获取中断 | 添加请求间隔、User-Agent 伪装、超时重试 |
| ECharts CDN 不可用 | 图表无法渲染 | 备选本地引入或使用其他图表库 |
| Playwright 浏览器安装失败 | 测试无法执行 | 使用 `npx playwright install`，备选 chromium only |

## 八、验收标准

1. ✅ Git 仓库可访问，包含完整代码与文档，提交记录清晰
2. ✅ 网页可在浏览器中正常打开，所有板块内容完整
3. ✅ 数据可视化图表正常渲染，数据与预处理结果一致
4. ✅ Playwright 测试全部通过，测试报告可查看
5. ✅ 网页截图清晰展示核心功能
6. ✅ 对话记录文档完整且已脱敏
7. ✅ README 文档包含项目说明、运行方式、技术栈

---

**计划确认：以上需求与方案已明确，进入执行阶段。**
