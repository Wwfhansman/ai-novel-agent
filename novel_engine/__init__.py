"""novel_engine — deterministic canon core for AI Novel Agent.

This package is the "strangler-fig" rewrite of the consistency layer. It treats
the chapter event log as the single source of truth and *derives* current state
by projection, instead of asking an LLM to hand-maintain entities/ledgers and
then checking them with regex.

It runs alongside the legacy scripts/ during migration and does not modify or
replace them. See novel_engine/README.md and docs/ENGINE.md.
"""

__all__ = [
    "events",
    "projection",
    "integrity",
    "ledger_health",
    "legacy",
    "diff",
    "profile",
]

__version__ = "0.1.0"
