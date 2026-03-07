/**
 * Boss直聘爬虫 - 连接已有Chrome版 (稳定版)
 */

const { chromium } = require('playwright');
const fs = require('fs');

const CONFIG = {
  keyword: '产品经理 AI',
  city: '北京',
  pageSize: 30,
  cookiesFile: 'cookies.json',
  outputFile: 'jobs.md',
  debugPort: 9222,
};

const CITY_CODE = {
  '北京': '101010100',
  '上海': '101020100',
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function connectToChrome() {
  try {
    const browser = await chromium.connectOverCDP(`http://localhost:${CONFIG.debugPort}`);
    console.log('✅ 已连接到Chrome浏览器');
    return browser;
  } catch (e) {
    console.log('❌ 连接失败，请确保Chrome已启动调试模式');
    return null;
  }
}

async function loadCookies(context) {
  if (fs.existsSync(CONFIG.cookiesFile)) {
    const cookies = JSON.parse(fs.readFileSync(CONFIG.cookiesFile, 'utf-8'));
    await context.addCookies(cookies);
    console.log('✅ Cookies已加载');
    return true;
  }
  return false;
}

// 获取当前活动的页面
async function getActivePage(browser) {
  const contexts = browser.contexts();
  for (const context of contexts) {
    const pages = context.pages();
    if (pages.length > 0) {
      return { page: pages[pages.length - 1], context };
    }
  }
  const context = await browser.newContext();
  const page = await context.newPage();
  return { page, context };
}

// 搜索岗位
async function searchJobs(page) {
  const cityCode = CITY_CODE[CONFIG.city] || '101010100';
  const searchUrl = `https://www.zhipin.com/web/geek/job?query=${encodeURIComponent(CONFIG.keyword)}&city=${cityCode}`;

  console.log(`🔍 搜索: ${CONFIG.keyword} - ${CONFIG.city}`);

  try {
    await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 60000 });
    await sleep(3000);

    // 检查是否需要验证
    const currentUrl = page.url();
    console.log(`📍 当前页面: ${currentUrl}`);

    if (currentUrl.includes('verify') || currentUrl.includes('captcha')) {
      console.log('⚠️ 需要验证，请在浏览器中完成验证后按回车继续...');
      await new Promise(resolve => process.stdin.once('data', resolve));
      await sleep(2000);
    }

    return true;
  } catch (e) {
    console.log('⚠️ 页面加载问题:', e.message);
    await sleep(3000);
    return true;
  }
}

// 解析岗位
async function parseJobs(page) {
  console.log('📋 正在解析岗位信息...');

  try {
    const jobs = await page.evaluate(() => {
      const jobCards = document.querySelectorAll('.job-card-wrapper, .job-list li');
      const results = [];

      jobCards.forEach(card => {
        try {
          const titleEl = card.querySelector('.job-name a, .job-title');
          const companyEl = card.querySelector('.company-name a, .company-text');
          const salaryEl = card.querySelector('.salary, .job-salary');
          const areaEl = card.querySelector('.company-area, .job-area');
          const tagEls = card.querySelectorAll('.tag-list li, .job-tags span');
          const welfareEl = card.querySelector('.company-tag-list, .company-tags');

          const title = titleEl?.innerText?.trim() || '';
          const link = titleEl?.href || '';
          const company = companyEl?.innerText?.trim() || '';
          const salary = salaryEl?.innerText?.trim() || '';
          const area = areaEl?.innerText?.trim() || '';

          const tags = Array.from(tagEls).map(t => t.innerText?.trim()).filter(Boolean);

          const welfare = welfareEl?.innerText?.trim() || '';

          if (title && company) {
            results.push({ title, company, salary, area, tags: tags.join(' | '), welfare, link });
          }
        } catch (e) {}
      });

      return results;
    });

    console.log(`✅ 解析到 ${jobs.length} 个岗位`);
    return jobs;
  } catch (e) {
    console.log('❌ 解析失败:', e.message);
    return [];
  }
}

// 导出Markdown
function exportToMarkdown(jobs) {
  let md = `# Boss直聘岗位搜索结果\n\n`;
  md += `**搜索条件**：${CONFIG.keyword} | ${CONFIG.city}\n`;
  md += `**抓取时间**：${new Date().toLocaleString('zh-CN')}\n`;
  md += `**岗位数量**：${jobs.length}\n\n---\n\n`;

  jobs.forEach((job, index) => {
    md += `## ${index + 1}. ${job.title}\n\n`;
    md += `| 属性 | 内容 |\n|------|------|\n`;
    md += `| 公司 | ${job.company} |\n`;
    md += `| 薪资 | ${job.salary} |\n`;
    md += `| 地区 | ${job.area} |\n`;
    md += `| 标签 | ${job.tags} |\n`;
    md += `| 链接 | [查看详情](${job.link}) |\n\n---\n\n`;
  });

  fs.writeFileSync(CONFIG.outputFile, md);
  console.log(`\n✅ 已导出: ${CONFIG.outputFile}`);
}

// 导出CSV
function exportToExcel(jobs) {
  const csvFile = 'jobs.csv';
  let csv = '\uFEFF序号,岗位名称,公司,薪资,地区,标签,链接\n';

  jobs.forEach((job, index) => {
    csv += `${index + 1},"${job.title}","${job.company}","${job.salary}","${job.area}","${job.tags}","${job.link}"\n`;
  });

  fs.writeFileSync(csvFile, csv);
  console.log(`✅ 已导出: ${csvFile}`);
}

// 主函数
async function main() {
  console.log('🚀 Boss直聘爬虫启动...\n');

  const browser = await connectToChrome();
  if (!browser) return;

  try {
    const { page, context } = await getActivePage(browser);

    // 加载cookies
    await loadCookies(context);

    // 搜索
    await searchJobs(page);

    // 解析
    const jobs = await parseJobs(page);

    if (jobs.length > 0) {
      exportToMarkdown(jobs);
      exportToExcel(jobs);
      console.log(`\n🎉 抓取完成！共 ${jobs.length} 个岗位`);
      console.log(`📄 查看: open jobs.md`);
    } else {
      console.log('\n⚠️ 未获取到数据，可能原因：');
      console.log('   1. 未登录 - 请在浏览器中登录Boss直聘');
      console.log('   2. 需要验证 - 请检查浏览器是否有验证弹窗');
      console.log('\n   登录后重新运行: node crawler.js search');
    }

  } catch (e) {
    console.log('❌ 执行出错:', e.message);
  }

  console.log('\n✅ 完成');
}

main().catch(console.error);
