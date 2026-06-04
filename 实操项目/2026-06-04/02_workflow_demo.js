/**
 * 实操3 Demo：Fan-out + Synthesize Workflow
 *
 * 功能：并行搜索多个 AI 话题 -> 综合生成一份简报
 *
 * 在 Claude Code 中运行方式：
 *   直接把这个脚本粘贴给 Claude，或保存后用 /workflow 调用
 *
 * 学习要点：
 *   1. Fan-out 模式：多个搜索并行执行
 *   2. Pipeline 模式：搜索结果 -> 格式化 -> 保存
 *   3. Schema 约束：结构化输出
 */

export const meta = {
  name: 'ai-briefing-demo',
  description: '并行搜索 AI 新闻并生成结构化简报',
  phases: [
    { title: '搜索', detail: '并行搜索多个 AI 话题' },
    { title: '生成', detail: '汇总搜索结果生成简报' },
    { title: '保存', detail: '写入 MD 文件' },
  ],
}

// ============================================================
// Phase 1: 并行搜索（Fan-out）
// ============================================================
phase('搜索')

const TOPICS = [
  {
    key: 'claude',
    query: 'Claude Code Agent SDK latest news 2026 June',
    label: 'Claude 相关',
  },
  {
    key: 'ai_agent',
    query: 'AI Agent development trends June 2026',
    label: 'AI Agent 趋势',
  },
  {
    key: 'tools',
    query: 'new AI developer tools MCP released 2026',
    label: '新工具',
  },
]

// 并行搜索所有话题
const searchResults = await parallel(
  TOPICS.map(topic => () =>
    agent(
      `搜索"${topic.query}"，返回 3-5 条最有价值的结果。
每条结果包含：标题、来源名称、链接、一句话摘要。`,
      {
        label: `search:${topic.key}`,
        phase: '搜索',
        schema: {
          type: 'object',
          properties: {
            items: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  title: { type: 'string' },
                  source: { type: 'string' },
                  url: { type: 'string' },
                  summary: { type: 'string' },
                  category: {
                    type: 'string',
                    enum: ['新技能', '新工具', '行业动态', '政策/投融资'],
                  },
                },
                required: ['title', 'source', 'url', 'summary'],
              },
            },
          },
          required: ['items'],
        },
      }
    )
  )
)

// 合并所有搜索结果
const allItems = searchResults
  .filter(Boolean)
  .flatMap(r => r.items || [])

log(`搜索完成，共获取 ${allItems.length} 条结果`)

// ============================================================
// Phase 2: 生成简报
// ============================================================
phase('生成')

// 按分类分组
const groups = {}
for (const item of allItems) {
  const cat = item.category || '行业动态'
  if (!groups[cat]) groups[cat] = []
  groups[cat].push(item)
}

// 取 Top 3
const sorted = [...allItems].sort((a, b) => {
  const priority = { '新技能': 4, '新工具': 3, '行业动态': 2, '政策/投融资': 1 }
  return (priority[b.category] || 0) - (priority[a.category] || 0)
})

const top3 = sorted.slice(0, 3)

// 生成 Markdown
const today = new Date()
const weekdays = ['日', '一', '二', '三', '四', '五', '六']
const dateStr = `${today.getFullYear()}年${String(today.getMonth() + 1).padStart(2, '0')}月${String(today.getDate()).padStart(2, '0')}日（星期${weekdays[today.getDay()]}）`

const categories = Object.keys(groups)
const tags = categories.map(c => {
  const emoji = { '新技能': '[新技能]', '新工具': '[新工具]', '行业动态': '[动态]', '政策/投融资': '[政策]' }
  return emoji[c] || c
}).join(' ')

let md = ''
md += `# AI 新闻简报 Demo -- ${dateStr}\n\n`
md += `> 共收录 ${allItems.length} 条 | 标签：${tags}\n\n`
md += '## 今日要闻 TOP 3\n\n'

top3.forEach((item, i) => {
  md += `### ${i + 1}. ${item.title}\n`
  md += `- **来源：** [${item.source}](${item.url})\n`
  md += `- **标签：** ${item.category || '行业动态'}\n`
  md += `- **摘要：** ${item.summary}\n`
  md += `- **为什么重要：** ${item.category === '新技能' ? '代表最新技术方向，值得关注' : item.category === '新工具' ? '提升开发效率的实用工具' : '影响行业格局的重要动态'}\n\n`
})

md += '## 分类内容\n\n'

for (const [cat, items] of Object.entries(groups)) {
  md += `### ${cat}\n`
  for (const item of items) {
    md += `- **[${item.title}]**：${item.summary}（[${item.source}](${item.url})）\n`
  }
  md += '\n'
}

md += '## 建议\n'
const suggestions = [
  '今日 TOP 1 内容值得深入学习，建议明天实操验证',
  '关注新工具分类中的项目，评估是否可以集成到你的三秘书系统中',
  '如果某个话题在多条新闻中重复出现，说明是行业热点，优先研究',
]
suggestions.forEach((s, i) => { md += `${i + 1}. ${s}\n` })

log(`简报生成完成，共 ${md.length} 字符`)

// ============================================================
// Phase 3: 保存
// ============================================================
phase('保存')

const dateFile = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
const outputPath = `E:/AI助手/实操项目/${dateFile}/demo_briefing.md`

// 用 Bash 创建目录并写入
await agent(
  `用 Bash 执行以下操作：
1. mkdir -p "E:/AI助手/实操项目/${dateFile}"
2. 将以下内容写入 "${outputPath}"：

\`\`\`markdown
${md}
\`\`\`

注意：内容较长，使用 Write 工具一次性写入。`,
  { label: 'save-briefing', phase: '保存' }
)

log(`简报已保存至: ${outputPath}`)

return {
  totalItems: allItems.length,
  top3: top3.map(t => t.title),
  outputPath,
  categories: Object.keys(groups),
}
