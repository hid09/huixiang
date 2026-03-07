/**
 * Boss直聘解析器 - 手动搜索版
 *
 * 使用方式：
 * 1. 在Chrome中手动搜索岗位
 * 2. 等岗位列表加载出来后
 * 3. 运行此脚本解析当前页面
 */

const { chromium } = require('playwright');
const fs = require('fs');

const CONFIG = {
  outputFile: 'jobs.md',
  debugPort: 9222,
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function connectToChrome() {
  try {
    const browser = await chromium.connectOverCDP(`http://localhost:${CONFIG.debugPort}`);
    console.log('✅ 已连接到Chrome浏览器');
    return browser;
  } catch (e) {
    console.log('❌ 连接失败');
    return null;
  }
}

async function parseJobs(page) {
  console.log('📋 正在解析当前页面...');

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
        const descEl = card.querySelector('.job-desc, .info-desc');

        const title = titleEl?.innerText?.trim() || '';
        const link = titleEl?.href || '';
        const company = companyEl?.innerText?.trim() || '';
        const salary = salaryEl?.innerText?.trim() || '';
        const area = areaEl?.innerText?.trim() || '';
        const tags = Array.from(tagEls).map(t => t.innerText?.trim()).filter(Boolean);
        const welfare = welfareEl?.innerText?.trim() || '';
        const desc = descEl?.innerText?.trim() || '';

        if (title && company) {
          results.push({ title, company, salary, area, tags: tags.join(' | '), welfare, desc, link });
        }
      } catch (e) {}
    });

    return results;
  });

  return jobs;
}

function exportToMarkdown(jobs) {
  let md = `# Boss直聘岗位搜索结果\n\n`;
  md += `**抓取时间**：${new Date().toLocaleString('zh-CN')}\n`;
  md += `**岗位数量**：${jobs.length}\n\n---\n\n`;

  jobs.forEach((job, index) => {
    md += `## ${index + 1}. ${job.title}\n\n`;
    md += `| 属性 | 内容 |\n|------|------|\n`;
    md += `| 公司 | ${job.company} |\n`;
    md += `| 薪资 | ${job.salary} |\n`;
    md += `| 地区 | ${job.area} |\n`;
    if (job.tags) md += `| 标签 | ${job.tags} |\n`;
    if (job.welfare) md += `| 福利 | ${job.welfare} |\n`;
    md += `| 链接 | [查看详情](${job.link}) |\n\n`;
    if (job.desc) md += `**描述**：${job.desc}\n\n`;
    md += `---\n\n`;
  });

  fs.writeFileSync(CONFIG.outputFile, md);
  console.log(`\n✅ 已导出: ${CONFIG.outputFile}`);
}

function exportToExcel(jobs) {
  const csvFile = 'jobs.csv';
  let csv = '\uFEFF序号,岗位名称,公司,薪资,地区,标签,福利,链接\n';

  jobs.forEach((job, index) => {
    csv += `${index + 1},"${job.title}","${job.company}","${job.salary}","${job.area}","${job.tags}","${job.welfare}","${job.link}"\n`;
  });

  fs.writeFileSync(csvFile, csv);
  console.log(`✅ 已导出: ${csvFile}`);
}

async function main() {
  console.log('🚀 Boss直聘解析器启动...\n');

  const browser = await connectToChrome();
  if (!browser) return;

  try {
    const contexts = browser.contexts();
    const context = contexts[0];
    const pages = context.pages();

    console.log(`📑 当前打开的页面: ${pages.length} 个\n`);

    // 找到Boss直聘的页面
    let targetPage = null;
    for (const page of pages) {
      const url = page.url();
      console.log(`  - ${url}`);
      if (url.includes('zhipin.com') && url.includes('job')) {
        targetPage = page;
      }
    }

    if (!targetPage) {
      console.log('\n⚠️ 未找到Boss直聘岗位列表页');
      console.log('请先在Chrome中：');
      console.log('1. 打开 https://www.zhipin.com');
      console.log('2. 搜索 "产品经理 AI"');
      console.log('3. 等岗位列表加载出来后，重新运行此脚本');
      return;
    }

    console.log('\n✅ 找到岗位列表页，开始解析...\n');

    const jobs = await parseJobs(targetPage);

    if (jobs.length > 0) {
      exportToMarkdown(jobs);
      exportToExcel(jobs);
      console.log(`\n🎉 解析完成！共 ${jobs.length} 个岗位`);
      console.log(`📄 查看结果: open jobs.md`);
    } else {
      console.log('\n⚠️ 未解析到岗位，请确保页面已加载完成');
    }

  } catch (e) {
    console.log('❌ 执行出错:', e.message);
  }
}

main().catch(console.error);
