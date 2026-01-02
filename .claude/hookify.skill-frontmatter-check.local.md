---
name: skill-frontmatter-check
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: SKILL\.md$
  - field: new_text
    operator: not_contains
    pattern: "---\nname:"
---

🚨 **SKILL.md 格式错误 - 缺少必需的 YAML Frontmatter！**

你正在创建/编辑 SKILL.md 文件，但**缺少必需的 frontmatter**。

## 正确格式 (REQUIRED)

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggers] - [what the skill does, in third person]
---

# Skill Title
...内容...
```

## 必需字段

| 字段 | 要求 |
|------|------|
| `name` | 只用字母、数字、连字符 (无括号/特殊字符) |
| `description` | 以 "Use when..." 开头，包含具体触发条件，第三人称 |

## 推荐做法

**手动创建 Skill 时，使用官方 `document-skills:skill-creator`：**

```bash
# 初始化 skill 模板
python3 ~/.claude/plugins/cache/anthropic-agent-skills/document-skills/*/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-dir>
```

**或在对话中：**
> "我想创建一个新 skill"
> Claude 会自动使用 skill-creator 指南

## 示例 (正确)

```yaml
---
name: stm32-f103-beginner
description: Use when learning STM32 from scratch, understanding GPIO, timers, interrupts, or debugging embedded issues. Trigger phrases include: STM32 GPIO, 定时器, 中断, 蜂鸣器不响.
---
```

**请添加正确的 frontmatter 后再继续！**
