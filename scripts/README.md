# Scripts

绝大部分旧脚本（`validate_novel_output.py`、`check_not_but.py`、`round_state_merge.py`、`smoke_test.py`、`validators/`）已被 `novel_engine` 取代——校验、句式扫描、状态合并、模板自检现在都走引擎：

```bash
python -m novel_engine check  projects/my-novel   # schema + 引用/时序完整性 + 账本健康 + 结构
python -m novel_engine patterns chapters/chNNN/final.txt   # AI 腔句式
python -m novel_engine txt      chapters/chNNN/final.txt   # TXT 格式/段落密度
python3 -m unittest discover -s novel_engine/tests -t .    # 内核测试
```

详见 [`docs/ENGINE.md`](../docs/ENGINE.md)。

## 仅剩的脚本

`compile_architect_context.py` —— 编剧层用，把当前项目状态压缩成 `novel-architect` 能读的上下文包（引擎暂未覆盖编剧层）：

```bash
python3 scripts/compile_architect_context.py projects/my-novel --init-missing
```

缺失时会补齐 `story_architecture.yml`、`thread_board.yml`、`completed_threads_log.yml`、`development_packs/`，并生成 `planning/context_packs/architect_context_pack_XXX.md`。
