# events/ — 引擎正史（append-only 事件日志）

当前状态由这里的事件**派生**，不要手写 entities/ledgers。

- 开新书：生成 book/entities/ledgers/planning 后，跑 `python -m novel_engine init <project>`，
  会从初始 entities/ledgers 生成 `bootstrap.yml`。
- 每写完一章：把本章 canon 变化写进 `chNNN.yml`（机械变化用类型化事件，叙事性用 note）。
- 词汇表见 `novel_engine/schemas/event.schema.json` 和 `docs/ENGINE.md`。
