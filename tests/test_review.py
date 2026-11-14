from reasoning_heuristics.generators import b4_e1
from reasoning_heuristics.review import coverage, pick_representative, render_item
from reasoning_heuristics.schema.item import compress, read_jsonl, write_jsonl


def test_packet_rendering_and_coverage(tmp_path):
    items, _ = b4_e1.generate("smoke", 11)
    chosen = pick_representative(items, 5)
    assert len(chosen) == 5 and len({it.cell for it in chosen}) == 5
    text = render_item(chosen[0])
    assert chosen[0].prompt in text and "| EXACT |" in text
    cov = coverage(items, b4_e1.cells({}))
    assert cov["covered"] == cov["designed_cells"] and cov["min_per_cell"] == 1
    path = tmp_path / "x.jsonl"
    write_jsonl(items, path)
    gz = compress(path)
    assert [it.to_json() for it in read_jsonl(gz)] == [it.to_json() for it in items]
    assert compress(path).read_bytes() == gz.read_bytes()  # deterministic
