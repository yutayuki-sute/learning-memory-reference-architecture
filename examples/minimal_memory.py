"""Executable toy example of scoped retrieval and a selective writeback gate.

No AI model, API, Google account, or persistence is involved. Records below are
synthetic. This illustrates control flow, not a production memory system.
"""

from __future__ import annotations

PROJECT_CATALOG = {"DEMO", "OTHER"}

PROJECT_MEMORY = [
    {
        "project_id": "DEMO",
        "key": "WRITEBACK_GATE",
        "kind": "PROCEDURE",
        "status": "ACTIVE",
        "text": "Require a candidate and evidence; deduplicate; append UNREVIEWED.",
        "tags": [],
    },
    {
        "project_id": "OTHER",
        "key": "WRITEBACK_GATE",
        "kind": "PROCEDURE",
        "status": "ACTIVE",
        "text": "Require a candidate and evidence; deduplicate; append UNREVIEWED.",
        "tags": [],
    },
    {
        "project_id": "DEMO",
        "key": "DEMO_RULE",
        "kind": "PRINCIPLE",
        "status": "ACTIVE",
        "text": "Use small tests before changing a workflow.",
        "tags": ["workflow"],
    },
    {
        "project_id": "OTHER",
        "key": "OTHER_RULE",
        "kind": "PRINCIPLE",
        "status": "ACTIVE",
        "text": "Never mix project notes.",
        "tags": ["workflow"],
    },
    {
        "project_id": "DEMO",
        "key": "OLD_RULE",
        "kind": "PRINCIPLE",
        "status": "RETIRED",
        "text": "Outdated instruction; must not be retrieved.",
        "tags": ["workflow"],
    },
]


def _normalized(text: str) -> str:
    """Simplistic exact-text deduplication, not semantic matching."""
    return " ".join(text.casefold().split())


def process_request(
    project_id: str,
    topic: str,
    candidate_learning: str = "",
    evidence: str = "",
    *,
    memories: list[dict] | None = None,
    experience_log: list[dict] | None = None,
) -> dict:
    """Resolve scope, read the active gate, retrieve, then optionally write.

    The caller supplies a *candidate* and its evidence. This example does NOT
    decide whether a model's assertion is true. Human review is separate.
    """
    if project_id not in PROJECT_CATALOG:
        raise ValueError("Unknown project: fail closed")

    records = PROJECT_MEMORY if memories is None else memories
    log = [] if experience_log is None else experience_log

    # Read operational procedure by metadata, independently of the topic.
    gates = [
        row for row in records
        if row["project_id"] == project_id
        and row["key"] == "WRITEBACK_GATE"
        and row["kind"] == "PROCEDURE"
        and row["status"] == "ACTIVE"
    ]
    if len(gates) != 1:
        raise RuntimeError("Expected exactly one active writeback gate: fail closed")

    retrieved = [
        row["text"] for row in records
        if row["project_id"] == project_id
        and row["kind"] != "PROCEDURE"
        and row["status"] == "ACTIVE"
        and topic in row["tags"]
    ]

    candidate = candidate_learning.strip()
    proof = evidence.strip()
    writeback = "SKIPPED"
    if candidate and proof:
        duplicate = any(
            row["project_id"] == project_id
            and _normalized(row["learning"]) == _normalized(candidate)
            for row in log
        )
        if duplicate:
            writeback = "DUPLICATE"
        else:
            log.append({
                "project_id": project_id,
                "learning": candidate,
                "evidence": proof,
                "review_status": "UNREVIEWED",
            })
            writeback = "APPENDED_UNREVIEWED"

    return {
        "project_id": project_id,
        "gate": gates[0]["key"],
        "retrieved": retrieved,
        "writeback": writeback,
        "experience_log": log,
    }


if __name__ == "__main__":
    import json

    result = process_request(
        "DEMO",
        "workflow",
        candidate_learning="Run a small test before revising a workflow.",
        evidence="Synthetic test record DEMO-001 (not an empirical claim)",
    )
    print(json.dumps(result, indent=2))
