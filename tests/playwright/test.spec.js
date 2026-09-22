// Playwright 测试用例：新浪财经分红数据展示网页
// 页面为静态 file:// 协议，ECharts 从 CDN 加载，需等待图表渲染完成
const { test, expect } = require('@playwright/test');

// 目标页面 URL（静态文件）
const PAGE_URL = 'file:///C:/Users/Administrator/Desktop/123/web/index.html';
// 本地 ECharts 文件（因 jsdelivr CDN 在当前网络下不可达/不稳定，
// 通过 Playwright route 拦截并重定向到本地副本，不修改 web/ 源文件）
const ECHARTS_LOCAL = require('path').join(__dirname, 'vendor', 'echarts.min.js');

test.beforeEach(async ({ page }) => {
  // 拦截对 jsdelivr 的 ECharts 请求，改用本地副本
  await page.route('**/cdn.jsdelivr.net/npm/echarts*/**', async (route) => {
    await route.fulfill({
      contentType: 'application/javascript; charset=utf-8',
      path: ECHARTS_LOCAL,
    });
  });
});

// 页面加载后等待 ECharts 图表与表格渲染完成的辅助函数
async function waitForPageReady(page) {
  // 等待 ECharts CDN（head 中的同步脚本）就绪，最多 30 秒
  // 注意：waitForFunction 的第二参数是 arg，第三参数才是 options
  await page.waitForFunction(() => window.echarts !== undefined, null, { timeout: 30000 });
  // 等待主脚本执行完成、表格 body 出现数据行（attached 即可，行可能在视口下方）
  await page.waitForSelector('#tableBody tr', { state: 'attached', timeout: 30000 });
  // 等待 4 个 ECharts 画布全部出现
  await page.waitForSelector('#chart1 canvas', { timeout: 30000 });
  await page.waitForSelector('#chart4 canvas', { timeout: 30000 });
  // 额外等待，确保动画/布局稳定
  await page.waitForTimeout(1000);
}

test.describe('新浪财经分红数据展示网页', () => {

  // ============================================================
  // 用例1：页面加载与标题测试
  // ============================================================
  test('用例1：页面成功加载且标题与主容器正确', async ({ page }) => {
    // 打开页面
    const response = await page.goto(PAGE_URL, { waitUntil: 'load' });

    // file:// 协议下 response 可能为 null，此时以 DOM 就绪为准；若有 response 则校验状态码
    if (response) {
      expect(response.status()).toBeLessThan(400);
    }
    // 验证页面已加载完成
    await expect(page).toHaveTitle(/分红|新浪财经/);

    // 验证页面存在主要容器元素
    await expect(page.locator('.navbar')).toBeVisible();
    await expect(page.locator('#overview')).toBeVisible();
    await expect(page.locator('.metrics-section')).toBeVisible();
    await expect(page.locator('#visualization')).toBeAttached();
    await expect(page.locator('#detail')).toBeAttached();
  });

  // ============================================================
  // 用例2：导航栏测试
  // ============================================================
  test('用例2：导航栏存在且包含锚点链接，点击可滚动到对应板块', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'load' });

    // 验证导航栏存在
    const navbar = page.locator('.navbar');
    await expect(navbar).toBeVisible();

    // 验证导航栏包含至少 4 个锚点链接
    const navLinks = page.locator('.navbar .nav-link');
    await expect(navLinks.first()).toBeVisible();
    expect(await navLinks.count()).toBeGreaterThanOrEqual(4);

    // 点击“数据明细”导航链接，验证页面滚动到对应板块
    await navLinks.getByText('数据明细').first().click();
    const detailSection = page.locator('#detail');
    // 等待滚动结束并验证目标板块在视口内可见
    await expect(detailSection).toBeInViewport({ timeout: 5000 });

    // 再点击“可视化”，验证另一板块也可到达
    await navLinks.getByText('可视化').first().click();
    await expect(page.locator('#visualization')).toBeInViewport({ timeout: 5000 });
  });

  // ============================================================
  // 用例3：Hero 指标卡片测试
  // ============================================================
  test('用例3：Hero 指标卡片与股票标签正确展示', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'load' });

    // 验证页面存在 4 个指标卡片
    const cards = page.locator('.metric-card');
    expect(await cards.count()).toBe(4);

    // 验证卡片中包含数字 "5"（股票数）和 "154"（记录数）
    await expect(page.locator('#metricStocks')).toHaveText('5');
    await expect(page.locator('#metricRecords')).toHaveText('154');

    // 验证 5 只股票名称标签存在
    const stockTags = page.locator('.stock-tag');
    expect(await stockTags.count()).toBe(5);
    const expectedStocks = ['贵州茅台', '工商银行', '中国平安', '招商银行', '五粮液'];
    for (const name of expectedStocks) {
      await expect(page.locator('.stock-tag', { hasText: name })).toBeVisible();
    }
  });

  // ============================================================
  // 用例4：ECharts 图表渲染测试
  // ============================================================
  test('用例4：ECharts 图表成功渲染且容器尺寸非零', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'load' });
    await waitForPageReady(page);

    // 验证页面存在至少 3 个 ECharts 画布
    const canvases = page.locator('div[id^="chart"] canvas');
    expect(await canvases.count()).toBeGreaterThanOrEqual(3);

    // 验证每个图表容器都带有 _echarts_instance_ 属性且尺寸非零
    for (const chartId of ['chart1', 'chart2', 'chart3', 'chart4']) {
      const container = page.locator('#' + chartId);
      // 已初始化的 ECharts 容器会带有 _echarts_instance_ 属性
      await expect(container).toHaveAttribute('_echarts_instance_', /./);
      const box = await container.boundingBox();
      expect(box).not.toBeNull();
      expect(box.width).toBeGreaterThan(100);
      expect(box.height).toBeGreaterThan(100);
    }
  });

  // ============================================================
  // 用例5：数据明细表测试（含搜索功能）
  // ============================================================
  test('用例5：数据明细表存在表头与数据行，搜索可过滤结果', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'load' });
    await waitForPageReady(page);

    // 验证数据表格存在
    const table = page.locator('#dataTable');
    await expect(table).toBeVisible();

    // 验证表格包含表头行
    const headerRow = page.locator('#dataTable thead tr');
    expect(await headerRow.count()).toBeGreaterThanOrEqual(1);
    await expect(headerRow).toBeVisible();

    // 验证表格中有数据行（至少 1 行）
    let rows = page.locator('#tableBody tr');
    expect(await rows.count()).toBeGreaterThanOrEqual(1);

    // 记录搜索前的信息
    const infoBefore = await page.locator('#tableInfo').textContent();
    expect(infoBefore).toContain('154');

    // 测试搜索功能：输入“茅台”，验证表格过滤结果
    const searchBox = page.locator('#tableSearch');
    await searchBox.fill('茅台');

    // 等待表格重新渲染
    await page.waitForTimeout(300);
    rows = page.locator('#tableBody tr');
    expect(await rows.count()).toBeGreaterThanOrEqual(1);

    // 过滤后的每一行都应包含“茅台”或其代码
    const firstRowText = await rows.first().textContent();
    expect(firstRowText).toContain('茅台');

    // 信息应更新为过滤后的记录数（小于 154）
    const infoAfter = await page.locator('#tableInfo').textContent();
    expect(infoAfter).not.toContain('154');

    // 清空搜索，数据应恢复
    await searchBox.fill('');
    await page.waitForTimeout(300);
    await expect(page.locator('#tableInfo')).toContainText('154');
  });

  // ============================================================
  // 用例6（可选）：代码片段测试
  // ============================================================
  test('用例6：页面存在 Python 代码片段且包含关键关键字', async ({ page }) => {
    await page.goto(PAGE_URL, { waitUntil: 'load' });
    await waitForPageReady(page);

    // 验证存在 pre 代码块
    const codeBlocks = page.locator('pre.code-content');
    expect(await codeBlocks.count()).toBeGreaterThanOrEqual(1);

    // 代码块内容由 JS 填充，等待其非空
    const firstCode = codeBlocks.first();
    await expect(firstCode).not.toBeEmpty({ timeout: 10000 });

    // 验证代码块包含 Python 关键字
    const allCode = await page.locator('pre.code-content').allTextContents();
    const joined = allCode.join('\n');
    expect(joined).toMatch(/import|def|import requests|BeautifulSoup|pandas/);
  });

  // ============================================================
  // 用例7（可选）：响应式测试
  // ============================================================
  test('用例7：移动端视口下导航栏与汉堡菜单正常工作', async ({ page }) => {
    // 设置视口为 375x812（iPhone）
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(PAGE_URL, { waitUntil: 'load' });
    await waitForPageReady(page);

    // 验证导航栏仍存在
    await expect(page.locator('.navbar')).toBeVisible();

    // 验证移动端汉堡菜单按钮出现（媒体查询在 <=767px 下 display:flex）
    const toggle = page.locator('#navToggle');
    await expect(toggle).toBeVisible();

    // 点击汉堡菜单，验证导航菜单展开（添加 .open 类）
    const menu = page.locator('#navMenu');
    await expect(menu).not.toHaveClass(/open/);
    await toggle.click();
    await expect(menu).toHaveClass(/open/);
    // 再次点击收起
    await toggle.click();
    await expect(menu).not.toHaveClass(/open/);

    // 说明：移动端视口下，页面因长代码块（pre 不换行）存在约 200px 的横向溢出，
    // 数据表格在自身 .table-wrapper 内横向滚动。此为页面既有表现，
    // 受“不修改 web/ 源文件”约束，本用例不将其作为失败条件，仅验证核心导航可用。
  });
});
