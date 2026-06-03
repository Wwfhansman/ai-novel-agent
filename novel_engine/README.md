# novel_engine

Deterministic canon core for AI Novel Agent. Treats the chapter **event log** as
the single source of truth and **derives** current state by projection, instead
of asking an LLM to hand-maintain `entities/`/`ledgers/` and checking them with
regex.

Runs alongside the legacy `scripts/` (strangler-fig migration); it does not
modify or replace them. Full design: [`docs/ENGINE.md`](../docs/ENGINE.md).

## Layout

```
novel_engine/
  schemas/event.schema.json   canonical event vocabulary (real JSON Schema)
  jsonschema_lite.py          zero-dependency schema validator
  events.py                   load + schema-validate events/chXXX.yml
  projection.py               the reducer: project(events) -> State
  integrity.py                referential + temporal integrity over the log
  ledger_health.py            overdue debts / stale foreshadowing (structure seed)
  context.py                  writer entering-state pack (bridge to creative layer)
  materialize.py              render projected state -> entities/ledgers files
  migrate.py                  one-shot legacy project -> events/ converter
  legacy.py                   adapter: old canon_delta.yml -> events (shadow diff)
  diff.py                     shadow: derived vs hand-written drift report
  profile.py + profiles/      genre/language thresholds (engine stays neutral)
  contracts.py                validate scene_spec / editor_verdict artifacts
  quality/prose_patterns.py   profile-driven AI-prose-tic scanner
  quality/prose_metrics.py    voice fingerprint + A/B compare
  quality/txt_format.py       profile-driven TXT format / paragraph-density check
  structure/                  read-pull / anti-shrink analysis over chapter records
  gate.py                     unified end-of-round gate (check / commit)
  scene/                      scene-level writing pipeline (plan + exemplars + per-scene packet)
  kit.py                      turnkey chapter production kit (rendered prompts + events template + steps)
  experiment.py               A/B (chapter-level vs scene-level) experiment package
  cli.py / __main__.py        command line
  tests/                      unittest suite + fixtures
```

## CLI

```bash
python -m novel_engine check        <project>                 # unified end-of-round gate (schema+integrity+health+structure)
python -m novel_engine commit        <project>                # gate, then materialize derived state in place
python -m novel_engine validate    <project>                  # schema + integrity over events/
python -m novel_engine project     <project>                  # print derived current state (JSON)
python -m novel_engine health      <project>                  # overdue debts / stale foreshadowing
python -m novel_engine context     <project> --chapter chNNN  # writer entering-state pack
python -m novel_engine materialize <project>                  # render entities/ledgers from events/
python -m novel_engine structure   <project>                  # read-pull / anti-shrink report
python -m novel_engine shadow      <project>                  # derived vs hand-written drift (read-only)
python -m novel_engine migrate     <project>                  # legacy canon_delta -> events/ (best-effort)
python -m novel_engine patterns    <file>                     # scan prose for AI-prose tics (profile-driven)
python -m novel_engine fingerprint <file>                     # voice fingerprint of a prose file
python -m novel_engine compare     <file_a> <file_b>          # prose A/B + voice-drift divergence
python -m novel_engine txt         <file>                     # profile-driven TXT format / density check
python -m novel_engine kit         <project> --chapter chNNN  # turnkey chapter production kit (rendered)
python -m novel_engine scene       <project> --chapter chNNN  # per-scene writing packets (JSON)
python -m novel_engine exemplars-init <project>               # scaffold style/exemplars.yml
python -m novel_engine experiment  <project> --chapter chNNN  # chapter-level vs scene-level A/B package
```

## Tests

```bash
python3 -m unittest discover -s novel_engine/tests -t .
```

No third-party dependencies. YAML uses PyYAML when present, else falls back to
`ruby` (same convention as the legacy scripts).
