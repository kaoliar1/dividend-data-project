// 独立截图脚本：使用 Playwright API 采集网页高质量截图
// 用法：node screenshot.js
// 说明：因 jsdelivr CDN 在当前网络下不可达，通过 page.route 拦截并重定向到本地 ECharts 副本
const { chromium } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

const PAGE_URL = 'file:///C:/Users/Administrator/Desktop/123/web/index.html';
const ECHARTS_LOCAL = path.join(__dirname, 'vendor', 'echarts.min.js');
const SHOT_DIR = 'C:/Users/Administrator/Desktop/123/screenshots';

async function waitChartsReady(page) {
  // 等待 ECharts 全局就绪
  await page.waitForFunction(() => window.echarts !== undefined, null, { timeout: 30000 });
  // 等待 4 个图表画布出现
  await page.waitForSelector('#chart1 canvas', { timeout: 30000 });
  await page.waitForSelector('#chart4 canvas', { timeout: 30000 });
  // 等待表格数据行渲染
  await page.waitForSelector('#tableBody tr', { state: 'attached', timeout: 30000 });
  // 额外等待 1 秒，确保图表动画与布局稳定
  await page.waitForTimeout(1000);
}

async function run() {
  // 确保截图目录存在
  fs.mkdirSync(SHOT_DIR, { recursive: true });

  const browser = await chromium.launch();

  // ---------- 桌面端 1920x1080 ----------
  const desktop = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 2, // 高清截图
  });
  const page = await desktop.newPage();

  // 拦截 jsdelivr ECharts 请求，改用本地副本
  await page.route('**/cdn.jsdelivr.net/npm/echarts*/**', async (route) => {
    await route.fulfill({
      contentType: 'application/javascript; charset=utf-8',
      path: ECHARTS_LOCAL,
    });
  });

  console.log('打开页面并等待图表渲染...');
  await page.goto(PAGE_URL, { waitUntil: 'load' });
  await waitChartsReady(page);

  // 1. 首页全貌（全页面截图）
  console.log('  -> 01-homepage-full.png');
  await page.screenshot({ path: path.join(SHOT_DIR, '01-homepage-full.png'), fullPage: true });

  // 2. Hero 区域特写（视口顶部，回到顶部）
  console.log('  -> 02-hero-section.png');
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(SHOT_DIR, '02-hero-section.png') });

  // 3. 可视化图表区域（滚动到图表板块后截图）
  console.log('  -> 03-charts-section.png');
  await page.locator('#visualization').scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(SHOT_DIR, '03-charts-section.png') });

  // 4. 数据明细表区域（滚动到表格板块后截图）
  console.log('  -> 04-data-table.png');
  await page.locator('#detail').scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.join(SHOT_DIR, '04-data-table.png') });

  await desktop.close();

  // ---------- 移动端 375x812 ----------
  console.log('移动端视口截图...');
  const mobile = await browser.newContext({
    viewport: { width: 375, height: 812 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
  });
  const mpage = await mobile.newPage();
  await mpage.route('**/cdn.jsdelivr.net/npm/echarts*/**', async (route) => {
    await route.fulfill({
      contentType: 'application/javascript; charset=utf-8',
      path: ECHARTS_LOCAL,
    });
  });
  await mpage.goto(PAGE_URL, { waitUntil: 'load' });
  await waitChartsReady(mpage);

  // 5. 移动端页面顶部截图
  console.log('  -> 05-mobile-view.png');
  await mpage.evaluate(() => window.scrollTo(0, 0));
  await mpage.waitForTimeout(500);
  await mpage.screenshot({ path: path.join(SHOT_DIR, '05-mobile-view.png') });

  await mobile.close();
  await browser.close();

  // 输出文件清单与大小
  console.log('\n截图完成，文件清单：');
  fs.readdirSync(SHOT_DIR)
    .filter(f => f.endsWith('.png'))
    .forEach(f => {
      const sz = fs.statSync(path.join(SHOT_DIR, f)).size;
      console.log(`  ${f}  (${(sz / 1024).toFixed(1)} KB)`);
    });
}

run().catch(err => {
  console.error('截图失败：', err);
  process.exit(1);
});
