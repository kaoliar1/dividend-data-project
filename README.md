# 新浪财经历史分红数据获取与预处理

> 实战作业项目：数据爬取 → 清洗预处理 → 可视化展示 → 自动化测试

## 项目简介

本项目从新浪财经获取 A 股上市公司历史分红数据，经过清洗与预处理后，通过网页进行可视化展示，并使用 Playwright 进行自动化测试。

## 考核点

- ✅ **Plan 模式确认需求** — 详见 `plan.md`
- ✅ **UI/UX 专业设计** — 详见 `web/` 目录
- ✅ **Playwright 网页测试** — 详见 `tests/playwright/` 目录

## 技术栈

| 环节 | 技术 |
|------|------|
| 数据获取 | Python 3 + requests + BeautifulSoup4 + lxml |
| 数据预处理 | Python 3 + pandas |
| 前端展示 | HTML5 + CSS3 + JavaScript (ES6+) |
| 数据可视化 | Apache ECharts 5 |
| 自动化测试 | Playwright (Node.js) |
| 版本控制 | Git |

## 项目结构

```
123/
├── plan.md                         # 需求确认计划（Plan模式）
├── README.md                       # 项目说明（本文件）
├── .gitignore                      # Git忽略规则
├── data/
│   ├── raw/
│   │   └── dividend_raw.csv        # 原始爬取数据（154条）
│   └── processed/
│       ├── dividend_clean.csv      # 清洗后数据
│       └── dividend_summary.json   # 统计摘要（可视化数据源）
├── src/
│   ├── fetch_dividend.py           # 数据获取脚本
│   └── preprocess.py               # 数据预处理脚本
├── web/
│   ├── index.html                  # 展示网页主页面
│   ├── css/
│   │   └── style.css               # 样式文件
│   └── js/
│       └── app.js                  # 交互与可视化脚本
├── tests/
│   └── playwright/
│       ├── package.json            # Playwright依赖
│       ├── playwright.config.js    # Playwright配置
│       └── test.spec.js            # 测试用例
├── docs/
│   └── conversation.md             # Agent对话记录（脱敏）
└── screenshots/                    # 网页截图
```

## 数据说明

### 数据源
新浪财经个股分红配股页面：
```
https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{股票代码}.phtml
```

### 覆盖股票（5只）

| 股票代码 | 股票名称 | 分红次数 | 累计派息(每10股/元) |
|----------|----------|----------|---------------------|
| 600519 | 贵州茅台 | 31 | 3256.60 |
| 000858 | 五粮液 | 31 | 392.69 |
| 601318 | 中国平安 | 41 | 267.80 |
| 600036 | 招商银行 | 28 | 198.46 |
| 601398 | 工商银行 | 23 | 47.88 |

### 数据规模
- 总记录数：154 条
- 时间范围：1999-05-28 ~ 2026-08-29
- 字段：股票代码、股票名称、公告日期、分红年度、送股、转增、派息税前、进度、除权除息日、股权登记日、红股上市日

## 快速开始

### 1. 数据获取与预处理

```powershell
# 安装依赖
pip install requests beautifulsoup4 lxml pandas

# 数据获取
python src/fetch_dividend.py

# 数据预处理
python src/preprocess.py
```

### 2. 查看网页展示

直接用浏览器打开 `web/index.html` 即可。

### 3. 运行 Playwright 测试

```powershell
cd tests/playwright
npm install
npx playwright install chromium
npx playwright test
```

## 预处理规则

1. **去空白**：去除所有字段的前后空白字符和 HTML 残留
2. **日期格式化**：统一为 `YYYY-MM-DD` 格式，无效日期标记为空字符串
3. **数值转换**：`--`、`不分配` 等非数值标记转为 0，数值字段转为 float
4. **缺失值处理**：日期缺失标记为空字符串，数值缺失转为 0
5. **数据去重**：按股票代码 + 公告日期 + 派息金额 组合去重
6. **分红年度推导**：按公告月份推导（1-6月公告对应上一年度年报分红，7-12月对应当年中期/特别分红）

## 交付物清单

| 编号 | 交付物 | 位置 | 状态 |
|------|--------|------|------|
| D1 | Git 仓库链接 | 远程仓库 | ⏳ 远程仓库待用户后续绑定推送 |
| D2 | 展示网页 | `web/index.html` | ✅ |
| D3 | 网页截图 | `screenshots/` | ✅ |
| D4 | 对话记录文档 | `docs/conversation.md` | ✅ |
| D5 | 数据获取脚本 | `src/fetch_dividend.py` | ✅ |
| D6 | 数据预处理脚本 | `src/preprocess.py` | ✅ |
| D7 | 原始数据 | `data/raw/dividend_raw.csv` | ✅ |
| D8 | 预处理后数据 | `data/processed/` | ✅ |
| D9 | Playwright 测试 | `tests/playwright/` | ✅ |
| D10 | 需求计划文档 | `plan.md` | ✅ |
| D11 | 项目说明文档 | `README.md` | ✅ |

### Git 远程仓库绑定说明

本地 Git 仓库已初始化并完成 5 次规范提交，远程仓库需用户手动绑定推送：

```powershell
# 1. 在 Gitee/GitHub 上创建空仓库（不要初始化 README）
# 2. 关联远程仓库
git remote add origin <你的仓库地址>
# 3. 推送
git push -u origin master
```

## 声明

本项目仅用于学习和实战作业，数据来源于新浪财经公开页面，请勿用于商业用途。
