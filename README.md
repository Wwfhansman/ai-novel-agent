# AI Novel Agent

AI Novel Agent 是一套面向长篇小说创作的 agent-native 写作框架。它不是网页应用，也不是"一键生成小说"的工具——而是把一本小说组织成一个文件系统项目：正文、设定、人物/势力/世界状态、伏笔、信息差都落在可审计的文件里。你对着 agent 说话，agent 执行工作流，文件保存长期记忆。

核心是 `novel_engine`：**正史是一份只增不改的事件日志（`events/`），当前状态由事件"算"出来（投影），而不是手工维护**。所以"变化记录"和"当前状态"不可能对不上——长篇写下去不失忆、不漂移。正文采用**场景级**写法，比章级更有体温、更少任务感。

## 怎么用（对着 agent 说话）

你不用敲命令。在你的 agent 工作台（OpenCode 等）里，对它说人话，它在后台读章纲、写正文、记事件、跑校验：

| 你想做什么 | 对 agent 说 |
|---|---|
| 开新书 | `用这个点子开一本新书：「一句话设定」` |
| 写下一章 | `写下一章`（或 `继续写` / `写 ch004`） |
| 检查质量 | `检查一下最近三章` |
| 加反转 / 改设定 | `给主角加个反转——他父亲其实还活着` |
| 开发后续剧情 | `帮我把后面 10 章铺开` |

> 下面的命令和结构是给想了解底层、或手动操作的人看的。**正常写作完全用不到。**

## 核心：引擎模型

```
events/  （只增不改的正史：本章造成了什么变化）
   │  投影（reducer，确定性）
   ▼
entities/ + ledgers/  （当前状态：人物/势力/地点/物品/伏笔/信息差/世界）
   │  ★派生产物，不手写——commit 从 events 重算并物化
```

- **`events/` 是唯一变化权威。** 每章写完，把本章的 canon 变化记成类型化事件（关系变了、谁知道了什么、势力动了、伏笔收了……）。
- **`entities/`、`ledgers/` 是算出来的。** `commit` 把所有事件折叠成当前状态写盘；手工改会被覆盖。
- **不会漂移。** "事件说 X 但状态是 Y"这种旧毛病，构造上不存在。
- **长对话不记混。** 每写一章，引擎从文件重新算出"进入本章时的状态"（entering-state）递给 writer——不靠对话记忆，换不换对话都一样。

## 一章怎么产

故事 DNA（创作宪法、长篇蓝图、初始人物、第一卷章纲）由 `novel-bootstrap` 从一句 seed 生成。之后逐章：

```
kit      取本章生产套件（entering-state + 逐场规格 + 文风范例）
 ↓
逐场写   场景级：先写够感官/情绪/织入，推进只是小料，结尾留外部动作
 ↓
缝合     连成整章 → chapters/chNNN/final.txt
 ↓
events   把本章变化记进 events/chNNN.yml（类型化事件 + note）
 ↓
check    schema + 引用/时序完整性 + 账本健康 + 结构 + 记漏
 ↓
commit   通过则把状态物化为派生 entities/ledgers
```

## 角色分工

引擎管记账（状态/连续性/门禁/度量），skill 管创作：

- **`novel-bootstrap`** — 从 seed 生成故事 DNA。
- **`novel-engine-write`**（默认）— 逐章场景级写作。
- **`novel-architect`** — 编剧层：撑大世界、排支线、控节奏和成长预算（防世界缩水）。
- **`novel-review`** — 冷读质量、文风、追读性、人物体温（引擎判断不了的部分）。
- **`novel-change`** — 中途改设定 / 加反转 / 变更管理。
- **`novel-memory-recheck`**（OpenCode subagent）— 读正文 + events，把漏记的关系/状态（含潜文本）补成事件。

## 项目结构

```
projects/<novel>/
  events/                ★正史：事件日志（bootstrap.yml + chXXX.yml）
  chapters/chXXX/         final.txt（正文）+ _kit/（生产套件）
  entities/              ★派生：characters / factions / locations / items / power_system
  ledgers/              ★派生：narrative_debts / foreshadowing / knowledge_state / world_state
  planning/              编剧层（手维护）：rolling_plan / story_architecture / thread_board / …
  book/                  全书：创作宪法、长篇蓝图（受保护）、读者模型、风格记忆
  style/  meta/          文风样本、模型路由、会话日志
```

## 引擎命令（进阶）

```bash
# 开新书 / 逐章
python -m novel_engine init   <project>                  # 种初始事件（bootstrap）
python -m novel_engine kit    <project> --chapter chNNN  # 一章生产套件
python -m novel_engine check  <project>                  # 统一门禁
python -m novel_engine commit <project>                  # 物化派生状态

# 体检
python -m novel_engine structure <project>               # 追读性 / 防缩水（节奏/张力/世界/弧线）
python -m novel_engine coverage  <project>               # 记漏检测（正文里关系变了却没记）
python -m novel_engine health    <project>               # 逾期债务 / 沉睡伏笔
python -m novel_engine project   <project>               # 打印派生的当前状态

# 文风（作用于正文文件）
python -m novel_engine txt <file>     # TXT 格式 / 段落密度
python -m novel_engine patterns <file>  # AI 腔句式
python -m novel_engine compare <a> <b>  # 两段正文文风对比 / 漂移

# 旧项目搬迁
python -m novel_engine shadow  <project>                 # 漂移量（只读）
python -m novel_engine migrate <project>                 # 旧 canon_delta → events/
```

完整命令、事件词汇表和迁移路径见 [docs/ENGINE.md](docs/ENGINE.md)；引擎化写作流程见 [docs/ENGINE_WORKFLOW.md](docs/ENGINE_WORKFLOW.md)。

## 开发

```bash
git clone https://github.com/Wwfhansman/ai-novel-agent.git
cd ai-novel-agent
python3 -m unittest discover -s novel_engine/tests -t .   # 内核测试
```

`novel_engine` 零第三方依赖（YAML 用 PyYAML，缺失时回退 ruby）。新项目由 `novel-bootstrap` 从 `templates/project/` 创建。

## 文档

- [确定性正史内核 novel_engine](docs/ENGINE.md)
- [引擎化写作流程](docs/ENGINE_WORKFLOW.md)
- [编剧层设计](docs/STORY_ARCHITECTURE.md) · [正史与安全规则](docs/CANON_AND_SAFETY.md) · [写作心法](docs/WRITING_CRAFT.md) · [模型路由](docs/MODEL_ROUTING.md)
- [历史方案归档](docs/archive/README.md)

## 仓库安全

这个仓库保存创作系统，不保存你的私人小说。`.gitignore` 默认忽略 `/projects/*`（示例项目除外）。真实小说需要 Git 备份时，建议放单独的私有仓库。

## License

尚未选择开源许可证。在添加许可证前，本仓库是 public source-available，但不是正式开源授权。
