"""A tiny, zero-dependency JSON Schema validator.

It implements the subset the engine needs: type, required, enum, const,
properties, additionalProperties (bool), items, minItems, and oneOf. This is
deliberately small — its job is to validate event objects against
schemas/event.schema.json at emit time, replacing the old "regex over Markdown"
approach with real structural validation.

It is NOT a full draft-07 implementation. If validation needs grow, swap in the
`jsonschema` package; the call sites only use validate().
"""

from __future__ import annotations

from typing import Any

_TYPE_CHECKS = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _type_ok(value: Any, types: Any) -> bool:
    if isinstance(types, str):
        types = [types]
    return any(_TYPE_CHECKS.get(t, lambda v: True)(value) for t in types)


def _validate(value: Any, schema: dict, path: str, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        return

    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path or '<root>'}: expected type {schema['type']}, got {type(value).__name__}")
        return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path or '<root>'}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path or '<root>'}: {value!r} not in enum {schema['enum']}")

    if "oneOf" in schema:
        matches = []
        branch_errors: list[list[str]] = []
        for index, branch in enumerate(schema["oneOf"]):
            local: list[str] = []
            _validate(value, branch, path, local)
            if not local:
                matches.append(index)
            branch_errors.append(local)
        if not matches:
            # Surface the branch that came closest (fewest errors) for a useful message.
            closest = min(branch_errors, key=len)
            errors.append(f"{path or '<root>'}: matched no oneOf branch; closest: {closest[0] if closest else 'unknown'}")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path or '<root>'}: missing required property '{key}'")
        if schema.get("additionalProperties") is False:
            allowed = set(props)
            for key in value:
                if key not in allowed:
                    errors.append(f"{path or '<root>'}: additional property '{key}' not allowed")
        for key, subschema in props.items():
            if key in value:
                _validate(value[key], subschema, f"{path}.{key}" if path else key, errors)

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path or '<root>'}: expected at least {schema['minItems']} item(s), got {len(value)}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate(item, item_schema, f"{path}[{index}]", errors)


def validate(value: Any, schema: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    _validate(value, schema, "", errors)
    return errors
