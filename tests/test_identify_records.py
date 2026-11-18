"""The response record, its JSON form, the join to items, and fits keyed by (model, condition, eval, domain)."""

import numpy as np
import pytest
from identify_helpers import patterned_items, plant, responses_from

from reasoning_heuristics.identify.engine import fit_all
from reasoning_heuristics.identify.likelihood import UnitModel
from reasoning_heuristics.identify.records import Response, join, read_responses, write_responses
from reasoning_heuristics.identify.units import Unit, clusters


def test_record_validation_and_round_trip(tmp_path):
    r = Response("i1", "h1", "openai/gpt-oss-20b", "ok", answer={"x1": True}, reasoning_tokens=812, condition="direct")
    assert Response.from_json(r.to_json()) == r
    with pytest.raises(ValueError):
        Response("i1", "h1", "m", "wrong-category")
    with pytest.raises(ValueError):
        Response("i1", "h1", "m", "parse_fail", answer="SAT")
    with pytest.raises(ValueError):
        Response.from_json({**r.to_json(), "surprise": 1})
    path = tmp_path / "r.jsonl.gz"
    write_responses([r, Response("i2", "h2", "m", "truncated", reasoning_tokens=32000)], path)
    back = read_responses(path)
    assert back[0] == r and back[1].category == "truncated"


def test_join_checks_hashes():
    items = [{"item_id": "a", "content_hash": "h", "presentation_hash": "p"}]
    assert join([Response("a", "h", "m", "ok", answer="YES")], items)[0][1] is items[0]
    with pytest.raises(ValueError):
        join([Response("a", "other", "m", "ok")], items)
    with pytest.raises(ValueError):
        join([Response("a", "h", "m", "ok", presentation_hash="q")], items)
    with pytest.raises(KeyError):
        join([Response("b", "h", "m", "ok")], items)


def test_clusters_join_sets_and_bases():
    items = [{"set_id": "s1", "base_hash": "b1"}, {"set_id": "s2", "base_hash": "b1"},
             {"set_id": "s2", "base_hash": "b2"}, {"set_id": "s3", "base_hash": "b3"}]
    c = clusters(items)
    assert c[0] == c[1] == c[2] != c[3]


def test_fit_all_keys_on_model_and_condition():
    rng = np.random.default_rng(0)
    items = patterned_items(300, rng)
    um = UnitModel(Unit("T_E0", "SAT", items))
    rs = responses_from(um, plant(um, {"B": 1.0}, 0.0, 0.3, rng), model="m1", condition="thinking")
    rs += responses_from(um, plant(um, {"C": 1.0}, 0.0, 0.3, rng), model="m1", condition="direct")
    out = fit_all(items, rs, n_boot=20, n_perm=0)
    assert set(out) == {("m1", "thinking", "T_E0", "SAT"), ("m1", "direct", "T_E0", "SAT")}
    w = out[("m1", "thinking", "T_E0", "SAT")]["fit"]["weights"]
    assert w["B"]["pi"] > 0.9
    w = out[("m1", "direct", "T_E0", "SAT")]["fit"]["weights"]
    assert w["C"]["pi"] > 0.9
