"""The lineage rule of docs/GENERATORS.md, as a test helper.

- A base item has source_hash null and base_hash = its own content_hash, unless its set was built
  on a base that is never shown on its own (A/H E2 ENT): then every item of the set is a root
  and they share one base_hash.
- A derived item's source_hash is the content_hash of the item it was manipulated from: an item
  of the same set, or, for evals built on another eval's items (A/H E8), an item of `external`.
  Its base_hash is its source's base_hash.
"""

from __future__ import annotations

from collections import defaultdict

UNEMITTED_BASES = {("A/H", "E2", "ENT")}  # (vertical, eval, cell prefix): the base is not an item


def lineage_problems(items, external=()) -> list[str]:
    errs = []
    by_set = defaultdict(list)
    for it in items:
        by_set[it.set_id].append(it)
    ext = {it.content_hash: it for it in external}
    for sid, members in by_set.items():
        here = {it.content_hash: it for it in members}
        for it in members:
            if it.source_hash is None:
                if it.base_hash != it.content_hash:
                    key = (it.vertical, it.eval_id, it.cell.split("/")[0])
                    if key not in UNEMITTED_BASES:
                        errs.append(f"{it.item_id}: a base item whose base_hash is not its content_hash")
                    elif len({m.base_hash for m in members}) != 1 or any(m.source_hash for m in members):
                        errs.append(f"{it.item_id}: items on an unemitted base must all be roots sharing one base_hash")
                continue
            src = here.get(it.source_hash) or ext.get(it.source_hash)
            if src is None:
                errs.append(f"{it.item_id}: source_hash {it.source_hash} is no item of its set (or of the source eval)")
            elif src.base_hash != it.base_hash:
                errs.append(f"{it.item_id}: base_hash differs from its source's")
    return errs
