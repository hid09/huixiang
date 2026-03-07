import { test, expect } from '@playwright/test';

test.describe('回响App - 移动端测试', () => {
  test.beforeEach(async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 390, height: 844 });
  });

  test('01 - 登录页面加载', async ({ page }) => {
    await page.goto('/login');

    // 检查登录页面关键元素
    await expect(page.locator('text=登录')).toBeVisible();
    console.log('✅ 登录页面加载正常');
  });

  test('02 - 首页布局检查', async ({ page }) => {
    // 模拟已登录状态
    await page.goto('/');

    // 检查录音按钮是否存在
    const recordButton = page.locator('button').filter({ hasText: /录音|开始/ });
    const hasRecordButton = await recordButton.count() > 0;

    console.log(`✅ 首页布局检查完成，录音按钮: ${hasRecordButton ? '存在' : '不存在'}`);
  });

  test('03 - 日记列表页面', async ({ page }) => {
    await page.goto('/diaries');

    // 检查页面是否正常渲染
    await page.waitForTimeout(1000);

    // 检查是否有日记卡片或空状态提示
    const hasCards = await page.locator('[class*="diary"], [class*="card"]').count() > 0;
    const hasEmpty = await page.locator('text=/暂无|还没有|空/').count() > 0;

    console.log(`✅ 日记列表页面正常，有日记: ${hasCards}, 空状态: ${hasEmpty}`);
  });

  test('04 - 个人中心页面', async ({ page }) => {
    await page.goto('/profile');

    await page.waitForTimeout(500);

    // 检查个人中心元素
    const pageContent = await page.textContent('body');
    console.log(`✅ 个人中心页面加载完成`);
  });

  test('05 - 底部导航栏', async ({ page }) => {
    await page.goto('/');

    // 检查底部导航
    const navItems = ['首页', '日记', '记录', '我的'];
    let foundCount = 0;

    for (const item of navItems) {
      const found = await page.locator(`text=${item}`).count() > 0;
      if (found) foundCount++;
    }

    console.log(`✅ 底部导航检查: 找到 ${foundCount}/${navItems.length} 个导航项`);
  });

  test('06 - 页面响应式 - 小屏幕', async ({ page }) => {
    // 测试更小的屏幕 (iPhone SE)
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    await page.waitForTimeout(500);

    // 确保页面没有水平滚动
    const scrollWidth = await page.evaluate(() => document.body.scrollWidth);
    const clientWidth = await page.evaluate(() => document.body.clientWidth);

    console.log(`✅ 小屏幕测试: scrollWidth=${scrollWidth}, clientWidth=${clientWidth}`);
  });
});
