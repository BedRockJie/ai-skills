# CLI 赋能讲义

## 1. 目标

这份讲义用于给团队快速赋能 4 类 AI CLI：

- Claude Code
- Codex
- Gemini CLI
- OpenCode
- Cursor CLI Agent

培训重点不是“问答”，而是 3 件事：

1. 用 CLI 管理本地项目和文件
2. 用统一的初始化机制加载项目上下文
3. 用 Plan 模式先规划，再执行，再验证

---

## 2. 一句话定位

| CLI | 更适合的定位 | 现场建议角色 |
|---|---|---|
| Claude Code | 稳健规划、长文推演、复杂约束梳理 | 方案师 / 审阅者 |
| Codex | 本地工程操作、补丁式改动、终端协作 | 主力开发执行器 |
| Gemini CLI | 超长上下文、搜索结合、多模态输入 | 大上下文分析器 |
| OpenCode | 多 agent 编排、Provider 路由、Plan/Build 分工 | 编排器 / 实验平台 |
| Cursor CLI Agent | IDE 规则复用、交互式审改、headless 自动化 | IDE 外延执行器 |

这个表不是绝对能力排序，而是实战中的默认分工。

---

## 3. 统一工作流

不管用哪个 CLI，统一采用同一套工作流：

1. 启动即初始化
2. 读取项目根指令文件
3. 装载项目 skills
4. 装载知识库和权威文档
5. 进入 Plan 模式
6. 经确认后再进入执行模式
7. 执行后必须验证结果

建议把这套流程作为团队 SOP，而不是把注意力放在单个模型的“提示词技巧”上。

---

## 4. Plan 模式是重点

Plan 模式的目标不是拖慢速度，而是防止模型直接改错。

一个合格的 Plan 模式至少要输出：

1. 任务理解
2. 假设与缺失信息
3. 将读取的文件和上下文
4. 变更范围
5. 风险点
6. 验证方法
7. 执行顺序

### 4.1 推荐口令

```text
先进入 Plan 模式，不要直接修改文件。
先扫描项目结构、关键配置、相关源码和说明文件。
给我一份执行计划，包含：
1. 你理解的目标
2. 你会读取哪些文件
3. 你准备修改哪些文件
4. 风险和边界
5. 验证步骤
确认后再执行
```

### 4.2 为什么 Plan 模式最重要

- 它把“会不会改代码”升级成“会不会做工程决策”
- 它强制模型先读上下文，再行动
- 它让团队更容易做权限边界和审计
- 它天然适合现场教学，因为学员能看见模型如何形成计划

---

## 5. 启动即初始化

### 5.1 推荐初始化顺序

1. 读取用户级配置
2. 读取项目级配置
3. 读取项目根指令文件
4. 读取项目角色 / 原则 / 技能
5. 识别当前工程类型
6. 进入 Plan 模式

### 5.2 工程类型要切换上下文

不同工程，初始化重点不同：

| 工程类型 | 初始化重点 |
|---|---|
| 新项目 0→1 | 目标、边界、目录结构、生成脚手架 |
| 存量维护 | 先读 README、配置、测试、历史提交 |
| GPU / CUDA | 先读构建脚本、编译器版本、硬件约束、性能指标 |
| 文档 / 知识库 | 先读规范、目录结构、权威来源、引用边界 |
| 流程 / 管理仓库 | 先读治理文件、角色文件、原则文件 |

不要让模型一启动就“凭常识”工作，必须先声明当前工程上下文。

---

## 6. Skills 和知识库怎么分工

### 6.1 Skills

Skill 是“方法”。它告诉 CLI：

- 什么时候触发
- 用什么步骤做
- 输出格式是什么
- 需要什么脚本或模板

适合沉淀：

- Code review 方法
- Git 提交流程
- 调试步骤
- 测试策略
- 文档模板

当前仓库已有技能示例：

- [skills/git/SKILL.md](/home/emb/workspces/code-nv/ai-skills/skills/git/SKILL.md)
- [skills/testing/SKILL.md](/home/emb/workspces/code-nv/ai-skills/skills/testing/SKILL.md)
- [skills/debugging/SKILL.md](/home/emb/workspces/code-nv/ai-skills/skills/debugging/SKILL.md)
- [skills/code-review/SKILL.md](/home/emb/workspces/code-nv/ai-skills/skills/code-review/SKILL.md)

### 6.2 知识库

知识库是“事实”。它告诉 CLI：

- 这个组织是谁
- 当前项目目标是什么
- 什么原则不能违反
- 哪些文件是权威来源

适合沉淀：

- 架构原则
- 领域知识
- 组织规则
- SOP
- 产品约束

### 6.3 最佳实践

- Skill 放“怎么做”
- 知识库放“依据什么做”
- 根引导文件只做 bootloader，不重复复制正文

---

## 7. `.agents` 和项目关键文件示例

你现在这台机器上，最适合现场演示的项目级上下文在 `segteamflow`。

### 7.1 根引导文件

- [AGENTS.md](/home/emb/workspces/code-nv/segteamflow/AGENTS.md)

这个文件的作用不是堆规则，而是定义启动顺序。它明确要求 agent 在做 substantive work 前按顺序加载：

1. `.agents/IDENTITY.md`
2. `.agents/PRINCIPLES.md`
3. 战略层文件
4. 月度目标拆解文件

这就是“CLI 启动即初始化”的最佳示例。

### 7.2 角色文件

- [IDENTITY.md](/home/emb/workspces/code-nv/segteamflow/.agents/IDENTITY.md)

它定义了 agent 的角色、分析风格、决策约束。现场可讲解：

- 角色不是人设，而是决策视角
- 角色文件用于限制输出风格和关注重点

### 7.3 原则文件

- [PRINCIPLES.md](/home/emb/workspces/code-nv/segteamflow/.agents/PRINCIPLES.md)

它定义了判断算法，例如：

- 结构优先于优化
- 机制优先于个人能力
- 清晰优先于灵活
- 可重复优先于完美

这类文件非常适合让 CLI 在 Plan 模式先做“机制审查”。

### 7.4 项目级角色 Prompt

Codex 项目里还存在按角色拆分的提示文件：

- [arch-xiaogao.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/arch-xiaogao.md)
- [dev-xiaozhang.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/dev-xiaozhang.md)
- [devops-xiaohe.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/devops-xiaohe.md)
- [pm-xiaoan.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/pm-xiaoan.md)
- [qa-xiaodong.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/qa-xiaodong.md)

这类文件适合做“角色化子代理”。

---

## 8. 5 类 CLI 的配置、Skills、MCP、历史记录

下面分成两类信息：

- `本机已核验`：我已在这台机器上看到
- `规范路径`：来自官方约定，现场如未安装需按实际核验

### 8.1 Codex

本机已核验：

- `~/.codex/config.toml`
- `~/.codex/history.jsonl`
- `~/.codex/rules/default.rules`
- `~/.codex/log/`
- `~/.codex/shell_snapshots/`
- 项目级 `.codex/prompts/`

你这台机器上的实际文件：

- [/home/emb/.codex/config.toml](/home/emb/.codex/config.toml)
- [/home/emb/.codex/history.jsonl](/home/emb/.codex/history.jsonl)
- [/home/emb/workspces/code-nv/segteamflow/.codex/prompts/dev-xiaozhang.md](/home/emb/workspces/code-nv/segteamflow/.codex/prompts/dev-xiaozhang.md)

已观察到的作用：

- `config.toml`：模型、信任目录、TUI 状态行
- `history.jsonl`：交互历史，字段包含 `session_id`、`text`、`ts`
- `.codex/prompts/`：项目内角色化上下文

适合讲的重点：

- Codex 非常适合“先读仓库，再改补丁”
- 它天然适合本地项目和文件操作
- 适合把项目 prompt 和工程规则沉淀到仓库里

### 8.2 Gemini CLI

本机已核验：

- `~/.gemini/settings.json`
- `~/.gemini/projects.json`
- `~/.gemini/trustedFolders.json`
- `~/.gemini/state.json`
- 项目级 `.gemini/settings.json`

你这台机器上的实际文件：

- [/home/emb/.gemini/settings.json](/home/emb/.gemini/settings.json)
- [/home/emb/workspces/code-nv/segteamflow/.gemini/settings.json](/home/emb/workspces/code-nv/segteamflow/.gemini/settings.json)

已观察到的作用：

- 全局 `settings.json`：认证和会话保留等全局行为
- 项目级 `settings.json`：当前仓库被配置为读取 `@AGENTS.md`
- `trustedFolders.json`：信任目录
- `projects.json`：项目级状态

这个项目的实际配置是：

```json
{
  "context": {
    "fileName": "@AGENTS.md"
  }
}
```

这意味着 Gemini 进入该仓库后，会把 `AGENTS.md` 作为项目初始化入口。

### 8.3 OpenCode

本机已核验：

- `~/.config/opencode/`
- `~/.local/share/opencode/opencode.db`
- `~/.local/state/opencode/prompt-history.jsonl`
- `~/.local/state/opencode/model.json`
- `~/.local/share/opencode/log/`

你这台机器上的实际文件：

- [/home/emb/.local/share/opencode/opencode.db](/home/emb/.local/share/opencode/opencode.db)
- [/home/emb/.local/state/opencode/prompt-history.jsonl](/home/emb/.local/state/opencode/prompt-history.jsonl)

已观察到的作用：

- `prompt-history.jsonl`：提示历史，字段包含 `input`、`mode`、`parts`
- `opencode.db`：会话和状态数据
- `log/`：运行日志

官方配置重点适合这样讲：

- OpenCode 支持全局 `~/.config/opencode/opencode.json`
- 支持项目级 `opencode.json`
- 支持 `.opencode/agents/` 或全局 agents 目录
- 支持内置 `plan` agent 和 `build` agent 分工
- 很适合作为“Plan/Build 分离”的示范工具

### 8.4 Claude Code

本机状态：

- 当前机器未检测到 `claude` 命令

规范路径和机制建议按 Claude Code 官方约定讲解：

- `~/.claude/settings.json`
- `.claude/settings.json`
- `.claude/settings.local.json`
- `CLAUDE.md`
- `~/.claude/agents/`
- `.claude/agents/`

适合讲的重点：

- `CLAUDE.md` 负责启动时加载记忆和项目指令
- `settings.json` 负责权限、环境变量、工具行为
- `/init` 用于初始化项目指导文件
- `/agents` 管理子代理
- `/mcp` 管理 MCP 连接

### 8.5 Cursor CLI Agent

官方已确认：

- 安装命令：`curl https://cursor.com/install -fsS | bash`
- CLI 入口是 `agent`
- 支持交互式模式和 headless 模式
- 支持文件操作、搜索、shell 命令
- 支持 MCP，并自动读取 `mcp.json`
- 支持规则目录 `.cursor/rules`
- 会读取项目根目录的 `AGENTS.md` 和 `CLAUDE.md`
- 支持恢复历史会话：`--resume [thread id]`、`cursor-agent resume`
- 支持列出历史会话：`cursor-agent ls`

本机状态：

- 当前机器未核验到 Cursor CLI 命令和本地配置目录

规范讲法建议：

- Cursor CLI 最大价值不是“又一个聊天窗口”，而是把 Cursor Agent 从 IDE 带到终端
- 如果团队已经在 IDE 里使用 Cursor 规则体系，CLI 可以直接复用 `.cursor/rules`
- 如果仓库已经有 `AGENTS.md`，Cursor CLI 也会把它作为规则来源之一
- 非交互模式适合脚本、CI、批量文档更新、安全检查

适合讲的重点：

- 交互模式：适合现场演示 plan、review、follow-up
- headless 模式：适合自动化流水线
- 规则系统：适合和 IDE 保持一致
- MCP：适合和现有 IDE 工具链共用

推荐现场口令：

```text
先不要写代码，先进入 planning。
请先读取 AGENTS.md、.cursor/rules 和当前项目关键配置。
给我一个执行计划，说明：
1. 你会读取哪些文件
2. 你准备如何修改
3. 风险点和验证步骤
确认后再执行
```

---

## 9. MCP 要怎么讲

MCP 不要讲成“高级功能”，而要讲成“CLI 的扩展总线”。

最简单的定义：

- Skill 解决“模型怎么做”
- MCP 解决“模型能连什么工具”

典型 MCP 场景：

- 连 GitHub / GitLab
- 连 Jira / 禅道
- 连数据库
- 连文档系统
- 连浏览器 / 搜索
- 连另一个 AI CLI

培训时建议强调 3 个判断：

1. 这个能力应该是 prompt，还是 tool？
2. 这个能力应该沉淀成 skill，还是沉淀成 MCP？
3. 这个能力是全局配置，还是项目配置？

经验判断：

- 只需要方法，不需要外部系统接入：用 skill
- 需要稳定接外部能力：用 MCP
- 只对某个仓库有效：用项目级配置
- 对所有项目都通用：用用户级配置

---

## 10. 每个模型的实战优势

下面是培训时更有用的“工程优势”，不是模型排行榜。

| 模型 / CLI | 实战优势 | 最适合交给它的活 |
|---|---|---|
| Claude Code | 长链路计划、需求拆解、文档组织强 | 先做 plan、审稿、方案评审 |
| Codex | 本地仓库操作强、补丁式修改稳 | 改代码、调脚本、处理文件 |
| Gemini CLI | 大上下文吞吐强、搜索与多模态结合强 | 快速读大仓、读长文、读图表/PDF |
| OpenCode | Agent 编排灵活、provider 可切换 | 多角色协作、Plan/Build 分层 |
| Cursor CLI Agent | 复用 IDE rules/MCP、交互式审改顺手 | IDE 外终端执行、自动化 agent |

建议团队默认分工：

- Claude / OpenCode plan agent 负责先规划
- Codex 负责主执行
- Gemini 负责大上下文补充分析
- Cursor 负责承接 IDE 规则到终端和自动化链路

---

## 11. 现场演示脚本

### 11.1 演示 A：CUDA 测试程序

目标：演示 CLI 如何在本地项目里先 plan，再读文件，再改代码，再验证。

推荐流程：

1. 进入 CUDA 项目目录
2. 明确要求先进入 Plan 模式
3. 让 CLI 扫描：
   - 构建脚本
   - `CMakeLists.txt` / `Makefile`
   - CUDA 源码
   - README
   - 测试脚本
4. 让它输出：
   - 编译路径
   - 运行路径
   - GPU 环境依赖
   - 改动点
   - 验证命令
5. 确认后再执行修改
6. 最后让它自己总结“改了什么、怎么验证的、还有什么风险”

推荐提示词：

```text
先进入 Plan 模式，不要直接改。
这是一个 CUDA 测试程序。
请先扫描构建脚本、CUDA 源码、运行入口和测试方式。
给我一个执行计划：
1. 你理解当前程序要验证什么
2. 你会读哪些文件
3. 你可能改哪些文件
4. 你准备怎么编译和运行
5. 风险点是什么
6. 你会如何验证性能或正确性
确认后再执行
```

演示重点：

- 模型不是直接生成 CUDA 代码
- 模型先识别工程结构和编译链
- Plan 模式能让大家看见“它为什么这么改”

### 11.2 演示 B：编写本文档

目标：演示 CLI 如何处理“文档生成 + 引用项目关键文件”。

推荐流程：

1. 在仓库根目录启动 CLI
2. 要求先读取：
   - `AGENTS.md`
   - `.agents/IDENTITY.md`
   - `.agents/PRINCIPLES.md`
   - 当前仓库已有 `skills/`
3. 让 CLI 先做大纲计划
4. 再让 CLI 产出文档
5. 再要求它补充：
   - 配置路径
   - skills / 知识库区别
   - MCP 位置
   - 历史记录位置
   - Plan 模式口令

推荐提示词：

```text
先进入 Plan 模式。
我要写一份面向团队的 CLI 赋能讲义。
重点包括 Claude Code、Codex、Gemini CLI、OpenCode、Cursor CLI Agent。
请先读取项目里的关键上下文文件，并输出文档大纲。
文档必须覆盖：
1. CLI 启动即初始化
2. 工程上下文切换
3. skills 和知识库如何提供
4. 配置、MCP、历史记录
5. 每个模型的优势
6. 两个现场示例
确认大纲后再开始写正文
```

---

## 12. 培训时要反复强调的 5 个原则

1. 不要让模型直接写，先让它进入 Plan 模式
2. 不要把所有规则都塞进一个大 prompt，应该拆成 bootloader、原则、skills、知识库
3. 不要只讲模型能力，要讲项目初始化机制
4. 不要只看“能不能改出来”，要看“能不能稳定复用”
5. 不要追求单一最佳 CLI，要做分工协同

---

## 13. 你这次培训最适合的主线

最推荐的讲法不是按工具顺序讲，而是按工程流程讲：

1. 为什么要 CLI 化
2. 什么叫启动即初始化
3. 什么叫 Plan 模式
4. `.agents` / `AGENTS.md` 如何给项目注入上下文
5. skills、知识库、MCP 分别负责什么
6. 四种 CLI 如何各司其职
7. 用 CUDA 示例演示工程执行
8. 用本文档示例演示知识沉淀

这样大家学到的是方法，而不是某个工具的菜单。
