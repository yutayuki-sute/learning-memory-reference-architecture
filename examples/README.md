# Run a minimal retrieval + writeback gate

This is a **small, synthetic, standard-library-only Python example** of the
control flow described in the [reference architecture](../README.md).

```bash
python examples/minimal_memory.py
python -m unittest discover -s tests -v
```

Python 3.10+ recommended. No credentials, connectors, model calls, network
requests, or third-party packages are needed.

## What the example shows

1. Resolve a project from an explicit catalog. Unknown projects **fail closed**.
2. Find exactly one `ACTIVE` operational `WRITEBACK_GATE` by metadata **before**
   selecting memories by topic. Missing or duplicate gates **fail closed**.
3. Retrieve only the current project's `ACTIVE` topic-matching records.
   `RETIRED` records and another project's records are excluded.
4. At writeback, require **both** a supplied candidate and supporting evidence.
   Skip if either is missing; deduplicate normalized exact text within a project.
5. Append only to an `experience_log` with `review_status=UNREVIEWED`. Do **not**
   turn an observation into durable memory automatically.

Example output contains `"writeback": "APPENDED_UNREVIEWED"`, the matching
project-scoped memory, and a new, unreviewed Experience record. The tests
exercise no-write cases, duplicate suppression, project isolation, and
fail-closed errors.

## Boundaries and limitations

- This is **not a ChatGPT integration** or a drop-in memory server.
- All sample records and evidence identifiers are invented for demonstration;
  they are **not** results from the private pilot.
- A caller supplies `candidate_learning` and `evidence`. The code cannot verify
  their truth, significance, or safety. A real system needs independent review,
  access controls, persistent storage, audit history, and failure handling.
- Deduplication uses normalized exact text; semantic duplicates can slip through.
- Storage is in-memory, and each invocation starts with synthetic examples.
  Nothing is persisted across runs.

The purpose is to make the **boundaries** executable, not to imply that a few
lines of Python establish reliable long-term AI memory.
