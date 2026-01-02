---
name: use-skill-creator
enabled: true
event: prompt
conditions:
  - field: user_prompt
    operator: regex_match
    pattern: (创建|create|新建|write|写).{0,20}(skill|技能)
---

📋 **创建 Skill 最佳实践提醒**

检测到你想创建 Skill。请使用以下工具之一：

## 推荐工具

| 场景 | 工具 | 说明 |
|------|------|------|
| **手动创建** | `document-skills:skill-creator` | ✅ Anthropic 官方标准，包含 init/package 脚本 |
| **从网站爬取** | `skill-seekers` | 自动从文档网站生成 skill |
| **TDD 方法论** | `superpowers:writing-skills` | 测试驱动开发创建 skill |

## 快速开始 (官方标准)

1. **初始化模板：**
   ```bash
   python3 ~/.claude/plugins/cache/anthropic-agent-skills/document-skills/*/skills/skill-creator/scripts/init_skill.py my-skill --path ~/.iflow/skills/
   ```

2. **编辑 SKILL.md** (必须包含 frontmatter)

3. **打包发布：**
   ```bash
   python3 ~/.claude/plugins/cache/anthropic-agent-skills/document-skills/*/skills/skill-creator/scripts/package_skill.py ~/.iflow/skills/my-skill
   ```

## Frontmatter 格式 (必需)

```yaml
---
name: skill-name
description: Use when [triggers] - [what it does, third person]
---
```

**继续操作，我会帮你使用正确的方法创建 Skill！**
