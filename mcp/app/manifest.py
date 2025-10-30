from __future__ import annotations
import json
import os
import difflib
from app.config import MANIFEST_PATH

# Keep the example inline; you can override with MANIFEST_PATH
DEFAULT_MANIFEST: list[dict] = [
    {"workflow": "Revenue Dashboard",
     "entrypoint": "extract_from_salesforce"}
]

def load_manifest() -> list[dict]:
    if MANIFEST_PATH and os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)
    return DEFAULT_MANIFEST

def _normalize(s: str) -> str:
    """
    Lightweight normalization: lowercase and strip non-alphanumerics.
    Turns 'Revenue Dashboard' -> 'revenuedashboard'.
    """
    s = s.strip().lower()
    return "".join(ch for ch in s if ch.isalnum())


def _best_fuzzy_match(
    target: str, candidates: list[str], cutoff: float = 0.65
) -> tuple[str | None, float]:
    """
    Return (best_candidate, score) using difflib on normalized strings.
    If no candidate meets the cutoff, returns (None, 0.0).
    """
    norm_target = _normalize(target)
    # map normalized -> original for stable display
    norm_map = { _normalize(c): c for c in candidates }

    # exact normalized match first
    if norm_target in norm_map:
        return norm_map[norm_target], 1.0

    # fuzzy compare normalized strings
    best = None
    best_score = 0.0
    for c in candidates:
        score = difflib.SequenceMatcher(None, norm_target, _normalize(c)).ratio()
        if score > best_score:
            best, best_score = c, score

    if best is not None and best_score >= cutoff:
        return best, best_score
    return None, 0.0


def match_workflow_fuzzy(name: str, manifest: list[dict], cutoff: float = 0.65) -> dict:
    """
    Fuzzy-match a workflow name against the manifest.

    Matching strategy:
      1) Case-insensitive exact match
      2) Normalized exact match (strip spaces/punct, lowercase)
      3) Fuzzy match (difflib) on normalized strings with a configurable cutoff

    Raises ValueError with a helpful message if nothing is close enough.
    """
    key = name.strip().lower()
    # 1) simple case-insensitive exact
    for m in manifest:
        if m["workflow"].strip().lower() == key:
            return m

    # 2 + 3) normalized exact or fuzzy
    candidates = [m["workflow"] for m in manifest]
    best, score = _best_fuzzy_match(name, candidates, cutoff=cutoff)
    if best is not None:
        for m in manifest:
            if m["workflow"] == best:
                return m

    available = ", ".join(sorted(candidates))
    raise ValueError(
        f"Unknown workflow: '{name}'. "
        f"No close match (cutoff={cutoff}). Available: {available}"
    )