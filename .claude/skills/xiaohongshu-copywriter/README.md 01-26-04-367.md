# 小红书爆款文案写作专家 (xiaohongshu-copywriter)

[![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com)
[![Author](https://img.shields.io/badge/author-jianguo-green.svg)](https://github.com)

> 基于 Claude Code 的专业小红书文案生成 Skill，支持 7 种爆款标题公式、5 种写作风格

---

## 功能特点

- **爆款标题生成** - 7 种标题公式，自动生成 10-20 个高点击率标题
- **黄金内容结构** - 5 段式爆款文案结构（开头、干货、体验、总结、互动）
- **多风格支持** - 情绪共鸣、干货实用、种草安利、反差震惊、紧迫感
- **智能 Emoji** - 根据内容类型自动匹配合适的表情符号
- **话题标签优化** - 自动生成精准的话题标签组合

---

## 快速开始

### 安装

将整个 `xiaohongshu-copywriter` 文件夹放入项目的 `.claude/skills/` 目录下：

```
your-project/
└── .claude/
    ├── settings.json
    └── skills/
        └── xiaohongshu-copywriter/
            ├── skill.yaml
            └── README.md
```

### 配置

在 `.claude/settings.json` 中注册：

```json
{
  "skills": [
    {
      "name": "xiaohongshu-copywriter",
      "description": "小红书爆款文案写作专家",
      "alias": ["xhs", "小红书", "xhs-copywriter"],
      "path": ".claude/skills/xiaohongshu-copywriter/skill.yaml"
    }
  ]
}
```

---

## 使用方法

### 方式一：手动调用

```
/xiaohongshu-copywriter 护肤品推荐
/xhs 旅游攻略
/小红书 职场干货
```

### 方式二：自动触发

当您的对话中包含以下关键词时，Skill 会自动触发：

- 小红书文案 / 小红书标题
- xhs文案 / xhs标题
- 爆款文案 / 小红书爆款
- 种草文案 / 笔记文案

---

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `style` | string | `auto` | 写作风格 |
| `length` | string | `medium` | 内容长度 |
| `title_count` | integer | `12` | 标题数量 (8-20) |
| `include_emoji` | boolean | `true` | 是否包含 Emoji |
| `target_audience` | string | `""` | 目标受众描述 |

### 写作风格 (style)

| 值 | 风格 | 适用场景 |
|----|------|----------|
| `emotional` | 情绪共鸣风 | 情感类、生活感悟 |
| `practical` | 干货实用风 | 教程、攻略、经验分享 |
| `recommendation` | 种草安利风 | 好物推荐、美食探店 |
| `contrast` | 反差震惊风 | 测评、对比类内容 |
| `urgent` | 紧迫感风 | 限时活动、优惠信息 |
| `auto` | 自动判断 | 根据关键词自动选择 |

### 内容长度 (length)

| 值 | 字数范围 | 适用场景 |
|----|----------|----------|
| `short` | 200-300字 | 简单种草、快速分享 |
| `medium` | 300-500字 | 标准笔记、日常分享 |
| `long` | 500-800字 | 详细攻略、深度测评 |

---

## 使用示例

### 示例 1：种草推荐

**输入：**
```
/xhs 平价护肤品 学生党
```

**输出：**
- 12 个爆款标题（覆盖 7 种公式）
- 适合学生党的平价护肤品推荐内容
- 精准的话题标签
- 配图和发布时间建议

### 示例 2：旅游攻略

**输入：**
```
/xiaohongshu-copywriter 成都旅游 攻略 3天 --style=practical --length=long
```

**输出：**
- 悬念制造型 + 干货实用风标题
- 详细的 3 天行程安排
- 实用的避坑指南
- 相关话题标签

### 示例 3：情感共鸣

**输入：**
```
/小红书 职场新人 加班
```

**输出：**
- 痛点共鸣型标题
- 引发共鸣的情感内容
- 互动引导设计

---

## 标题公式

Skill 内置 7 种爆款标题公式：

| 公式类型 | 模板示例 |
|----------|----------|
| 数字冲击型 | `7个护肤技巧，我后悔没早知道` |
| 悬念制造型 | `没想到这个竟然是这样的` |
| 痛点共鸣型 | `谁懂啊！熬夜护肤的痛` |
| 对比反差型 | `用前vs用后，差距太大了` |
| 情绪共鸣型 | `救命！这个太好哭了` |
| 利益诱惑型 | `省钱攻略，立省5000` |
| 时间紧迫型 | `最后3天，错过等一年` |

---

## 输出格式

```markdown
# 📝 小红书爆款文案

## 💡 爆款标题（10-15个）
📌 **数字冲击型**
1. [标题1]
2. [标题2]
...

## 📄 完整内容（推荐标题：[标题名称]）
[黄金开头]
[干货展开]
[个人体验]
[价值总结]
[引导互动]

## 🏷️ 话题标签
#标签1 #标签2 #标签3 ...

## ✨ 优化建议
- [配图建议]
- [发布时间建议]
- [互动策略建议]
```

---

## 文件结构

```
xiaohongshu-copywriter/
├── skill.yaml      # Skill 配置文件
└── README.md       # 使用说明文档
```

---

## 更新日志

### v1.2.0 (2026-02-27)
- 新增 `triggers` 自动触发配置
- 支持关键词和意图两种触发方式

### v1.1.0 (2026-02-27)
- 新增 `author` 和 `tags` 元信息
- 新增 `title_count`、`include_emoji`、`target_audience` 参数
- 优化参数描述和示例

### v1.0.0
- 初始版本
- 支持 7 种标题公式
- 支持 5 种写作风格

---

## 许可证

MIT License

---

## 作者

jianguo

如有问题或建议，欢迎反馈！
