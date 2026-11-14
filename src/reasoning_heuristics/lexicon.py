"""Deterministic naming: vertex/variable labels, people, and the entailment lexicon.

- Labels are a prefix plus a two-digit number 10-99 (C §1.2): every label has the same
  shape, so swapping labels never changes the token multiset under the proxy tokenizer.
- Fixed-width SAT names x01..xNN (A/H §2.8).
- People are three-letter names (A/H rooms framing).
- The entailment lexicon (B4/C4 §2.10) is a pool of objects and properties. It is split
  20/80 into dev and test partitions *before* generation, by a fixed hash of each word,
  so dev and test items never share a name or a property.
"""

from __future__ import annotations

import hashlib

import numpy as np


def two_digit_labels(prefix: str, k: int, rng: np.random.Generator) -> list[str]:
    if k > 90:
        raise ValueError("at most 90 two-digit labels")
    nums = rng.choice(np.arange(10, 100), size=k, replace=False)
    return [f"{prefix}{int(x)}" for x in nums]


def fixed_width_names(prefix: str, k: int) -> list[str]:
    width = max(2, len(str(k)))
    return [f"{prefix}{i:0{width}d}" for i in range(1, k + 1)]


PEOPLE = (
    "Ann Ben Cal Dan Eve Fay Gus Hal Ivy Jay Kim Lee Max Ned Oli Pam Ray Sam Tom Una "
    "Val Wes Zoe Abe Bea Cy Deb Ed Flo Gil Hugh Ida Jo Kit Liz Mo Nat Ora Pat Rex "
    "Sue Ted Uma Vic Wyn Al Bo Di Em Fred Gwen Hans Iris Jim Kay Lou Meg Nell Otto Pia"
).split()


def people(k: int, rng: np.random.Generator) -> list[str]:
    if k > len(PEOPLE):
        raise ValueError("not enough people names")
    return [PEOPLE[i] for i in sorted(rng.choice(len(PEOPLE), size=k, replace=False))]


# --- entailment lexicon -------------------------------------------------------------------

OBJECTS = (
    "box jar cup pen bag hat cap mug key map bell lamp coat ring bowl vase belt sock shoe "
    "rope sack drum fork kite card book tray pipe sail flag coin boot comb fan net pot rug "
    "tent van cart bike boat jug lid pan pin pot tub urn wig axe bat cone dial disk gem"
).split()
PROPERTIES = (
    "red blue green heavy light cold warm big small round square soft hard old new clean "
    "dirty wet dry full empty open shut dark bright loud quiet thin thick smooth rough sharp "
    "flat tall short long wide narrow plain fancy"
).split()
# People theme: a name and a place or state phrase ("Ana is at the front desk").
PHRASES = (
    "at the front desk", "on the phone", "in the garden", "wearing gloves", "in the kitchen",
    "at the station", "on the train", "in the library", "reading a book", "holding a map",
    "near the door", "at the window", "on the roof", "in the car", "wearing a hat", "carrying a bag",
    "in the hall", "at the market", "on the bridge", "in the office", "wearing boots", "holding a cup",
    "at the gate", "on the stairs", "in the attic", "near the pond", "at the table", "on the bench",
    "in the shed", "holding a lamp",
)

# Machine-facts lexicon for A/H ENT: each device has one state word.
DEVICES = {
    "lamp": "lit", "alarm": "armed", "bell": "ringing", "fan": "spinning", "door": "open",
    "pump": "running", "valve": "open", "motor": "running", "gauge": "high", "heater": "on",
    "buzzer": "sounding", "gate": "closed", "light": "flashing", "switch": "up", "sensor": "active",
    "relay": "closed", "timer": "set", "dial": "turned", "lever": "down", "screen": "on",
}


def _dedupe(words: tuple[str, ...] | list[str]) -> list[str]:
    return list(dict.fromkeys(words))


def partition_of_word(word: str) -> str:
    """20/80 dev/test partition by a fixed hash of the word."""
    h = int(hashlib.sha256(("lexicon-v1:" + word).encode()).hexdigest(), 16)
    return "dev" if h % 5 == 0 else "test"


def lexicon(kind: str, split: str) -> list[str]:
    pool = {"objects": OBJECTS, "properties": PROPERTIES, "devices": tuple(DEVICES),
            "names": tuple(PEOPLE), "phrases": PHRASES}[kind]
    return [w for w in _dedupe(pool) if partition_of_word(w) == split]
