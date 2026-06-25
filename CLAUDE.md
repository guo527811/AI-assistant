# 项目说明

## 我的身份
- 我是 AI Agent 开发学习者，正在找工作
- 目标城市：上海（60%），其他城市（40%）
- 目标岗位：AI Agent 开发 / 大模型应用 / 提示工程

## 项目结构
- `E:/AI助手/新闻简报/` — 每日 AI 新闻（新闻秘书产出）
- `E:/AI助手/学习资料/每日学习/` — Claude Code 学习笔记（学习秘书产出）
- `E:/AI助手/学习资料/学习进度.md` — 学习进度追踪表
- `E:/AI助手/求职/岗位追踪/` — 岗位汇总（找工作秘书产出）
- `E:/AI助手/求职/我的简历-2026-06-05更新版.md` — 最新简历
- `E:/AI助手/求职/技能差距分析.md` — 持续更新的技能差距
- `E:/AI助手/rag/` — RAG 知识库系统
- `E:/AI助手/实操项目/` — 练习代码
- `E:/AI助手/配置/` — 关键词、邮箱配置、学习偏好

## 三秘书系统
三个定时 Agent 每日自动运行：
- 🗞️ 新闻秘书 (7:57) — 搜索新闻 → 简报 → 邮件 → RAG索引
- 💼 找工作秘书 (8:08) — 扫描岗位 → JD分析 → 技能差距 → 简历建议
- 📚 学习秘书 (9:03) — 搜索教程 → 学习笔记 → 更新进度 → RAG索引

## 技术栈
- Python 3.13（路径：`C:\Program Files\Python313\python.exe`）
- 大模型：DeepSeek V4 Pro（通过 Anthropic 兼容接口）
- RAG：LangChain + ChromaDB + HuggingFace Embeddings
- 邮件：163 邮箱 SMTP

## 常用命令
```bash
# RAG 索引
python "c:/Users/lenovo/Desktop/test/rag/rag_cli.py" index --collection news --dir "E:/AI助手/新闻简报/YYYY-MM-DD/"
python "c:/Users/lenovo/Desktop/test/rag/rag_cli.py" index --collection learning --file "E:/AI助手/学习资料/每日学习/YYYY-MM-DD-Claude-Code学习.md"
python "c:/Users/lenovo/Desktop/test/rag/rag_cli.py" index --collection jobs --dir "E:/AI助手/求职/岗位追踪/"

# RAG 检索
python "c:/Users/lenovo/Desktop/test/rag/rag_cli.py" search --collection news --query "关键词"

# 发送邮件
python "E:/AI助手/send_email.py" "邮件主题" "E:/AI助手/新闻简报/YYYY-MM-DD/今日AI新闻.md"

# 运行作业脚本
python "E:/AI助手/实操项目/agent_keyword_scanner.py"
python "E:/AI助手/实操项目/news_search_loop.py"
```

## 我的偏好
IMPORTANT: 以下规则必须遵守，不得例外。

- 回答问题用中文。代码注释用中文。
  - 正确：`# 获取最近 7 天的目录列表`
  - 错误：`# get recent 7 days dir list`
- 教学从简单开始，不要一上来就高级内容。
  YOU MUST 先讲"是什么"再讲"为什么"最后讲"怎么做"。
- 每次学习生成教学笔记到 `E:/AI助手/学习资料/每日学习/`，方便复习。
- 每个新概念用生活化的例子解释。
  - 正确："CLAUDE.md 像给新同事的入职手册"
  - 错误："CLAUDE.md 是项目级配置元数据文件"

## 禁止操作
IMPORTANT: 以下操作除非我明确要求，否则绝对不能做。

- 不要修改 `E:/AI助手/配置/邮箱配置.json` 中的密码
- 不要删除 `E:/AI助手/求职/` 下的简历文件
- 不要修改 `.env` / `.pem` / `credentials.*` 文件
- 不要执行 `git push --force` 或 `rm -rf`
- git commit 只在明确要求时执行

## 文件路径注意事项
- Windows 系统，路径用 `/` 或 `\`，不要在 Bash 里混用
- E 盘路径在 Bash 中写 `E:/AI助手/`（不是 `/e/AI助手/`）
- Python 路径在 Bash 中写 `/c/Program Files/Python313/python.exe`

## 踩过的坑（每次新坑请追加）
1. Hook 格式错误导致启动崩溃 — `.claude/settings.json` 中的 hooks 必须符合 JSON Schema
2. Windows/Linux 路径不一致 — 本地是 Windows，云服务器是 Linux
3. 权限提示阻塞无人值守 — CI/CD 场景用 `bypassPermissions`
4. Cron 任务 7 天自动过期 — 需要定期续期

## MCP Server
- `learning-progress` — 学习进度查询工具，配置在 `.mcp.json`
  - 3 个工具：`get_learning_progress` / `get_learning_detail` / `count_learning_hours`
