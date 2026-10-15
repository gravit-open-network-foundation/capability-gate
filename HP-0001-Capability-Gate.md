# HP-0001: Capability Gate (Frontier Capability State), v0.1

Status: draft with reference implementation and tests (`src/`, `tests/`, 9 tests passing). Not yet reviewed externally.

## 1. Inputs
- capability `c`
- policy `P` with a revision and three **disjoint** sets: `allowed`, `frontier`, `forbidden`, plus `override_quorum ≥ 2`
- action hash `h`: SHA3-256 of the concrete action
- optional verifier decision `D`, bound to `h`, with verdict `true | false | null` (as in CANON-RES-012) and state
- optional overrides `O`: approvals from authorities, bound to `h`

## 2. States
`SAFE`, `FRONTIER`, `UNSAFE`, `UNKNOWN`. The state is a function of `(c, P, D, O, h)`, not of `c` alone.

## 3. Rules
1. **Base:** `c ∈ allowed → SAFE`; `c ∈ forbidden → UNSAFE`; `c ∈ frontier → FRONTIER`; otherwise `UNKNOWN`.
2. **Override:** `UNSAFE → FRONTIER` only if at least `override_quorum` **distinct** authorities approved this `h`. An override never leads directly to `SAFE`.
3. **Settlement:** from `FRONTIER`:
   - verdict `true` and state Verified Fact → `SAFE`, for this action only;
   - verdict `false` → `UNSAFE`;
   - verdict `null`, no decision, or a decision bound to another action → stays `FRONTIER`.
4. **Permission:** only `SAFE` permits the action.

## 4. Invariants (each covered by a test)
| Invariant | Test |
|---|---|
| I1 Disjoint policy | `test_disjoint_policy_required` |
| I2 Fail-closed: UNKNOWN, FRONTIER and UNSAFE never permit | `test_unknown_is_not_permitted`, `test_only_safe_permits` |
| I3 No settlement without a Verified Fact | `test_frontier_settles_only_on_verified_fact` |
| I4 Binding: evidence for another action is ignored | `test_decision_must_be_bound_to_action` |
| I5 Override needs a distinct quorum and never skips verification | `test_override_needs_distinct_quorum_and_never_reaches_safe_directly`, `test_quorum_below_two_rejected` |
| I6 Determinism: same inputs, same content-addressed record | `test_deterministic_record` |
| I7 No silent crossing: every evaluation is appended to a hash-chained journal; a rewrite is detected | `test_journal_detects_rewrite` |

## 5. Changes against the source artifact
- UNKNOWN is a real state: the policy no longer covers everything.
- The frontier is its own set, not the boundary of `allowed`. This removes double states.
- The verifier verdict is three-valued (`null` = no verdict), not `{0,1}`.
- An override requires a quorum and never reaches SAFE directly.
- Status changed from "Complete / Ready" to "draft with tests".

## 6. Where it connects
- **Gravit Verifier:** produces the decision `D`.
- **History Keeper:** can anchor the journal head with independent timestamps.
- **OVAIC:** a candidate shared test case.
- **Proof-of-Control (LF Decentralized Trust):** a concrete answer to "did the agent stay within its controls, and who allowed crossing a boundary". It fits our planned comment.
