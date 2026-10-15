import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from capability_gate import *

P = {"revision": "r1", "allowed": ["read"], "frontier": ["pay"], "forbidden": ["self_replicate"], "override_quorum": 2}
H = "a" * 64

def dec(verdict, state="Verified Fact", h=H):
    return {"action_hash": h, "state": state, "verdict": verdict, "decision_id": "d1"}

def test_disjoint_policy_required():
    with pytest.raises(PolicyError):
        classify("x", {**P, "allowed": ["pay"]})

def test_unknown_is_not_permitted():
    r = evaluate("browse_darkweb", H, P)
    assert r["state"] == UNKNOWN and not r["permitted"]

def test_only_safe_permits():
    for cap, d in [("pay", None), ("pay", dec(None)), ("self_replicate", dec(True)), ("x", dec(True))]:
        assert not evaluate(cap, H, P, d)["permitted"]
    assert evaluate("read", H, P)["permitted"]

def test_frontier_settles_only_on_verified_fact():
    assert evaluate("pay", H, P, dec(True))["state"] == SAFE
    assert evaluate("pay", H, P, dec(True, "Probabilistic Assessment"))["state"] == FRONTIER
    assert evaluate("pay", H, P, dec(False))["state"] == UNSAFE
    assert evaluate("pay", H, P, dec(None))["state"] == FRONTIER

def test_decision_must_be_bound_to_action():
    r = evaluate("pay", H, P, dec(True, h="b" * 64))
    assert r["state"] == FRONTIER and "not bound" in r["reason"]

def test_override_needs_distinct_quorum_and_never_reaches_safe_directly():
    one = [{"authority": "A", "action_hash": H}, {"authority": "A", "action_hash": H}]
    assert evaluate("self_replicate", H, P, overrides=one)["state"] == UNSAFE
    two = [{"authority": "A", "action_hash": H}, {"authority": "B", "action_hash": H}]
    assert evaluate("self_replicate", H, P, overrides=two)["state"] == FRONTIER
    assert evaluate("self_replicate", H, P, dec(True), two)["state"] == SAFE  # still needs a verified fact

def test_quorum_below_two_rejected():
    with pytest.raises(PolicyError):
        classify("read", {**P, "override_quorum": 1})

def test_deterministic_record():
    assert evaluate("pay", H, P, dec(True)) == evaluate("pay", H, P, dec(True))

def test_journal_detects_rewrite():
    j = Journal()
    for cap in ("read", "pay", "x"):
        j.append(evaluate(cap, H, P))
    assert j.verify()
    j.entries[1]["record"]["state"] = SAFE
    assert not j.verify()
