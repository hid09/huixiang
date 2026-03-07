/**
 * 阿里云百炼 API 连通性测试
 * 文档参考: https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions
 */

import OpenAI from 'openai';
import dotenv from 'dotenv';

// 加载环境变量
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

dotenv.config({ path: join(__dirname, '.env') });

const client = new OpenAI({
  apiKey: process.env.DASHSCOPE_API_KEY,
  baseURL: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  timeout: 60000, // 60秒超时
});

async function testQwenPlus() {
  console.log('🧪 测试 qwen-plus 模型...\n');

  try {
    const completion = await client.chat.completions.create({
      model: 'qwen-plus',
      messages: [
        { role: 'user', content: '你好，请用一句话介绍你自己。' }
      ],
    });

    console.log('✅ 调用成功！\n');
    console.log('📝 模型回复:');
    console.log(completion.choices[0].message.content);
    console.log('\n📊 使用情况:');
    console.log(`   - Prompt tokens: ${completion.usage.prompt_tokens}`);
    console.log(`   - Completion tokens: ${completion.usage.completion_tokens}`);
    console.log(`   - Total tokens: ${completion.usage.total_tokens}`);

  } catch (error) {
    console.log('❌ 调用失败！\n');
    console.log('错误信息:', error.message);
    if (error.response) {
      console.log('状态码:', error.response.status);
      console.log('响应数据:', error.response.data);
    }
  }
}

async function testQwenMax() {
  console.log('\n🧪 测试 qwen-max 模型...\n');

  try {
    const completion = await client.chat.completions.create({
      model: 'qwen-max',
      messages: [
        { role: 'user', content: '你好，请用一句话介绍你自己。' }
      ],
    });

    console.log('✅ 调用成功！\n');
    console.log('📝 模型回复:');
    console.log(completion.choices[0].message.content);

  } catch (error) {
    console.log('❌ 调用失败！\n');
    console.log('错误信息:', error.message);
  }
}

// 运行测试
console.log('═══════════════════════════════════════');
console.log('  阿里云百炼 API 连通性测试');
console.log('═══════════════════════════════════════\n');

await testQwenPlus();
await testQwenMax();

console.log('\n═══════════════════════════════════════');
console.log('  测试完成');
console.log('═══════════════════════════════════════');
