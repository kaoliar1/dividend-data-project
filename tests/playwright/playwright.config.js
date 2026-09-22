// Playwright 配置文件
// 对新浪财经分红数据展示网页进行自动化测试
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  // 测试目录（当前目录）
  testDir: './',
  // 测试文件匹配
  testMatch: '*.spec.js',
  // 全局超时：每个用例 60 秒（ECharts CDN 冷加载可能较慢）
  timeout: 60000,
  // 预期断言超时
  expect: {
    timeout: 15000,
  },
  // 失败时重试（CI 场景），本地默认不重试
  retries: 0,
  // 并行：串行执行，避免 file:// 与 ECharts CDN 加载互相干扰
  workers: 1,
  // 截图：仅失败时截图
  use: {
    actionTimeout: 10000,
    navigationTimeout: 15000,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
  },
  // 测试报告：html + line
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['line'],
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
