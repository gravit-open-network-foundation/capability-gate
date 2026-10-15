# Capability Gate

A small, fail-closed primitive for AI agents: may this agent use this capability for this exact action?

- Policy lists `allowed`, `frontier` and `forbidden` capabilities (disjoint, with a revision).
- Anything not listed is `UNKNOWN` and is not permitted.
- A `frontier` capability is permitted only for one action, and only when an independent verifier returns a Verified Fact bound to that action ([GEVP](https://datatracker.ietf.org/doc/draft-gravit-gevp/), signed result `true | false | null`).
- A forbidden capability can be reopened only by a quorum of distinct authorities, and even then it must pass verification.
- Every evaluation is a content-addressed record in a hash-chained journal, so no boundary is crossed silently.

Specification: [HP-0001-Capability-Gate.md](HP-0001-Capability-Gate.md). Each invariant has a test.

```bash
pip install pytest && pytest -q tests
```

Status: draft v0.1, not yet externally reviewed. Corrections are welcome and will be credited.

Gravit Open Network Foundation · Apache 2.0
