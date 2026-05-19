# AI Novel Agent

AI Novel Agent is an agent-native framework for writing long-form fiction with LLM agents.

It is not a web app, not a SaaS product, and not a one-click novel generator. It is a file-based creative operating system that helps an AI agent plan, write, review, and maintain a long novel over many chapters without relying on chat history as memory.

The project is currently an MVP protocol: skills, templates, schemas, documentation, and a small example project.

## Why This Exists

Long novels fail under naive AI writing workflows for predictable reasons:

- The model writes a decent single chapter, then loses long-term continuity.
- Characters drift or act only to serve the plot.
- Foreshadowing and reader expectations are forgotten.
- The world stops reacting unless the protagonist is present.
- Chat history becomes an invisible and unreliable memory layer.
- Similarity-based RAG retrieves text that looks related but is not narratively relevant.

AI Novel Agent takes a different approach:

> The novel project itself is the memory system.

Instead of treating the previous text as a blob to retrieve from, the framework stores the story as layered project files: book-level constraints, volume state, chapter summaries, canon deltas, entity state, narrative debts, knowledge visibility, world state, and rolling plans.

## Core Ideas

### Files As Database

Every novel is a project folder. The files are the source of truth, and agent conversations are temporary workspaces.

```text
projects/my-novel/
  book/
  volumes/
  arcs/
  chapters/
  entities/
  ledgers/
  planning/
  style/
  meta/
```

### Structured Memory Over Vector Search

The framework prefers structured and semi-structured memory:

- `entities/characters.yml` records current character goals, intent, knowledge, and relationships.
- `ledgers/narrative_debts.yml` records what the reader is waiting for.
- `ledgers/knowledge_state.yml` records who knows what.
- `ledgers/world_state.yml` records external pressure, factions, resources, and consequences.
- `planning/rolling_plan.yml` records the next 9-15 chapters.

Full chapter text is still kept, but it is used for precise lookback rather than as the primary memory layer.

### Context Pack Before Writing

Before an agent writes a chapter, it must generate a visible `context_pack.md`.

The context pack records:

- which files were read
- why they were read
- key takeaways
- relevant old chapter lookbacks
- active narrative debts
- character intent
- knowledge visibility
- world pressure
- forbidden moves
- required updates after writing

This makes writing inputs auditable and reproducible.

### Canon Safety

The project defines source-of-truth rules.

Examples:

- Chapter text lives in `chapters/chXXX/final.txt`.
- Chapter-level change logs live in `canon_delta.yml`.
- Current character state lives in `entities/characters.yml`.
- Current world state lives in `ledgers/world_state.yml`.
- Future intent lives in `planning/rolling_plan.yml`.

`canon_delta.yml` is a change log, not the current state table.

## What Is Included

```text
ai-novel-agent/
  docs/                 Project design and protocol docs
  skills/               Agent skills for writing workflows
  schemas/              Field specs for structured memory files
  templates/            Blank novel project template
  projects/
    example-project/    Minimal sanitized example project
  scripts/              Placeholder for future automation
```

### Core Skills

- `novel-bootstrap`: initialize a new novel from a seed idea.
- `novel-write`: write the next chapter or three-chapter round with context packs and memory updates.
- `novel-review`: cold-start review, continuity checks, source-of-truth checks, and quality review.
- `novel-change`: safely handle mid-story ideas, setting changes, outline revisions, and retcons.

### Project Template

`templates/project/` contains a complete blank project structure, including:

- book-level memory
- volume memory
- arc memory
- chapter files
- entity state
- dynamic ledgers
- rolling plans
- style memory
- metadata and checkpoint placeholders

### Example Project

`projects/example-project/` is a tiny sanitized example. It demonstrates the protocol without becoming a real novel repository.

Real novel projects should be private by default. The included `.gitignore` ignores `/projects/*` except the example project.

## Quick Start

### 1. Clone The Repository

```bash
git clone https://github.com/Wwfhansman/ai-novel-agent.git
cd ai-novel-agent
```

### 2. Create A Private Novel Project

Copy the blank template:

```bash
cp -r templates/project projects/my-novel
```

On Windows PowerShell:

```powershell
Copy-Item -Recurse templates/project projects/my-novel
```

`projects/my-novel` is ignored by Git by default.

### 3. Use An Agent With The Skills

Ask your agent to use the appropriate skill:

```text
Use skills/novel-bootstrap to initialize projects/my-novel from this seed:
"A young lamp repairer discovers the city lamps preserve forgotten memories."
```

Then continue with:

```text
Use skills/novel-write to write round 001 for projects/my-novel.
```

For review:

```text
Use skills/novel-review to cold-start review projects/my-novel.
```

For mid-story changes:

```text
Use skills/novel-change to evaluate this idea and integrate it safely:
"The protagonist's father may be part of the lighthouse memory core."
```

## Recommended Workflow

```text
Bootstrap from seed
→ Generate initial project memory
→ Plan a 9-15 chapter rolling window
→ Write one 3-chapter round
→ Generate round and chapter context packs
→ Write chapter draft/final text
→ Generate summary and canon_delta
→ Merge current state into entities, ledgers, and planning
→ Cold-start review
→ Continue or run change management
```

The default writing unit is a three-chapter round. Each chapter still gets its own context pack and memory update.

## Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [MVP Scope](docs/MVP_SCOPE.md)
- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Memory Model](docs/MEMORY_MODEL.md)
- [Context Pack](docs/CONTEXT_PACK.md)
- [Canon And Safety](docs/CANON_AND_SAFETY.md)
- [Workflows](docs/WORKFLOWS.md)
- [File Formats](docs/FILE_FORMATS.md)
- [Development](docs/DEVELOPMENT.md)

## Repository Safety

This repository is designed to open-source the system, not your private fiction.

By default:

```gitignore
/projects/*
!/projects/.gitkeep
!/projects/example-project/
!/projects/example-project/**
```

If you want Git checkpoints for a real novel, keep that novel in a separate private repository or adjust the ignore rules intentionally.

## Current Status

MVP file protocol is implemented:

- Four core skills exist under `skills/`.
- Blank project template exists under `templates/project/`.
- Structured memory schemas exist under `schemas/`.
- Sanitized example project exists under `projects/example-project/`.
- Documentation describes the design, memory model, workflows, context packs, and canon safety rules.

Not included yet:

- CLI automation
- Web or desktop UI
- Database backend
- Vector retrieval
- Multi-user collaboration
- Publishing integrations

## Roadmap

Near-term:

- Test the protocol on a private 30-chapter experiment.
- Add lightweight validation scripts for YAML structure and required files.
- Add a project creation helper.
- Add context pack compilation helpers.

Later:

- Local workspace UI.
- Export tools.
- Optional database-backed project store.
- Reader feedback ingestion.
- Model-specific adapters.

## License

No license has been selected yet.

Until a license is added, this repository is public source-available but not formally open-source licensed. Choose a license such as MIT or Apache-2.0 before encouraging external reuse or contributions.

