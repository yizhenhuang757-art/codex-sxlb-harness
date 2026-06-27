#!/usr/bin/env python3
"""Recall likely skill clans and families for sxlb intake, planning, and dispatch."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "skills" / "family-trigger-index.json"
DEFAULT_CLAN_REGISTRY = ROOT / "skills" / "skill-clans.json"
DEFAULT_INVENTORY = ROOT / "skills" / "skill-inventory.generated.md"
MAX_REASON_MATCHES = 5
DEFAULT_SKILL_LIMIT = 3


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("families"), list):
        raise ValueError("family trigger index must contain a families list")
    return payload


def load_clan_lookup(path: Path = DEFAULT_CLAN_REGISTRY) -> dict[str, str]:
    payload = load_clan_registry(path)
    lookup: dict[str, str] = {}
    for clan in payload.get("clans", []):
        clan_name = str(clan.get("clan", ""))
        for family in clan.get("families", []):
            lookup[str(family)] = clan_name
    return lookup


def load_clan_registry(path: Path = DEFAULT_CLAN_REGISTRY) -> dict[str, Any]:
    if not path.exists():
        return {"clans": [], "max_clan_candidates": 2}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload.get("clans"), list):
        raise ValueError("clan registry must contain a clans list")
    return payload


def load_skill_inventory(path: Path = DEFAULT_INVENTORY) -> list[dict[str, str]]:
    if not path.exists():
        return []
    records: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0] in {"lifecycle", "---"}:
            continue
        lifecycle, family, offices, skill, source, path_cell, note = cells
        records.append(
            {
                "lifecycle": lifecycle,
                "family": f"family:{family}",
                "offices": offices,
                "skill": skill.strip("`"),
                "source": source,
                "path": path_cell.strip("`"),
                "note": note,
            }
        )
    return records


def term_matches(term: str, haystack: str) -> bool:
    needle = normalize(term)
    if not needle:
        return False
    return needle in haystack


def loose_text(value: str) -> str:
    return normalize(re.sub(r"[-_/]+", " ", value))


def loose_term_matches(term: str, haystack: str) -> bool:
    needle = loose_text(term)
    target = loose_text(haystack)
    return bool(needle) and needle in target


def normalize_semantic_keywords(values: list[str] | None) -> list[str]:
    keywords: list[str] = []
    for value in values or []:
        for part in re.split(r"[,，;；]", value):
            keyword = normalize(part)
            if keyword and keyword not in keywords:
                keywords.append(keyword)
    return keywords


def score_entry(
    entry: dict[str, Any],
    *,
    text: str,
    semantic_keywords: list[str] | None,
    phase: str | None,
    office: str | None,
) -> tuple[float, list[str]]:
    semantic = normalize_semantic_keywords(semantic_keywords)
    haystack = normalize(" ".join([text, *semantic]))
    family = str(entry.get("family", ""))
    family_terms = [family]
    if family.startswith("family:"):
        family_terms.extend(part for part in re.split(r"[-/:]", family.removeprefix("family:")) if part)
    triggers = [str(item) for item in entry.get("triggers", [])] + family_terms
    negatives = [str(item) for item in entry.get("negative_triggers", [])]
    matched = [term for term in triggers if term_matches(term, haystack)]
    negative_matches = [term for term in negatives if term_matches(term, haystack)]
    if not matched:
        return 0.0, []

    score = 0.35 + min(len(matched), 4) * 0.12
    phases = {str(item).casefold() for item in entry.get("phases", [])}
    if phase and phase.casefold() in phases:
        score += 0.08
    owners = {str(item) for item in entry.get("recall_owners", [])}
    if office and office in owners:
        score += 0.05
    if semantic and any(term_matches(term, " ".join(semantic)) for term in matched):
        score += 0.06
    score -= min(len(negative_matches), 3) * 0.12
    return max(0.0, min(score, 0.95)), matched[:MAX_REASON_MATCHES]


def build_family_lookup(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(entry.get("family", "")): entry for entry in registry.get("families", [])}


def clan_signal_terms(clan: dict[str, Any], family_lookup: dict[str, dict[str, Any]]) -> list[str]:
    terms = [
        str(clan.get("clan", "")),
        str(clan.get("title", "")),
        str(clan.get("use_when", "")),
    ]
    for family in clan.get("families", []):
        family_name = str(family)
        terms.append(family_name)
        if family_name.startswith("family:"):
            terms.extend(part for part in re.split(r"[-/:]", family_name.removeprefix("family:")) if part)
        entry = family_lookup.get(family_name, {})
        terms.extend(str(item) for item in entry.get("triggers", []))
    return terms


def score_clan(
    clan: dict[str, Any],
    *,
    text: str,
    semantic_keywords: list[str] | None,
    family_lookup: dict[str, dict[str, Any]],
) -> tuple[float, list[str]]:
    semantic = normalize_semantic_keywords(semantic_keywords)
    haystack = normalize(" ".join([text, *semantic]))
    matched = [term for term in clan_signal_terms(clan, family_lookup) if term_matches(term, haystack)]
    if not matched:
        return 0.0, []
    semantic_text = " ".join(semantic)
    semantic_matches = [term for term in matched if semantic_text and term_matches(term, semantic_text)]
    score = 0.32 + min(len(matched), 6) * 0.08 + min(len(semantic_matches), 3) * 0.05
    return max(0.0, min(score, 0.95)), matched[:MAX_REASON_MATCHES]


def skill_matches_family_signal(skill: dict[str, str], text: str, semantic_keywords: list[str]) -> bool:
    haystack = normalize(" ".join([text, *semantic_keywords]))
    signals = [skill["skill"], skill["note"], skill["source"]]
    return any(loose_term_matches(signal, haystack) for signal in signals if signal)


def build_skill_candidates(
    family_candidates: list[dict[str, Any]],
    *,
    text: str,
    semantic_keywords: list[str],
    inventory_path: Path = DEFAULT_INVENTORY,
    skill_limit: int = DEFAULT_SKILL_LIMIT,
) -> list[dict[str, Any]]:
    inventory = load_skill_inventory(inventory_path)
    family_order = {candidate["family"]: index for index, candidate in enumerate(family_candidates)}
    candidates: list[dict[str, Any]] = []
    for record in inventory:
        if record["family"] not in family_order:
            continue
        if record["lifecycle"] not in {"active", "active-via-family"}:
            continue
        family_candidate = family_candidates[family_order[record["family"]]]
        signal_bonus = 0 if skill_matches_family_signal(record, text, semantic_keywords) else 1
        candidates.append(
            {
                "skill": record["skill"],
                "family": record["family"],
                "clan": family_candidate["clan"],
                "path": record["path"],
                "lifecycle": record["lifecycle"],
                "source": record["source"],
                "offices": record["offices"],
                "reason": f"selected via {record['family']} inside {family_candidate['clan']}",
                "activation": "candidate-only",
                "_sort": (family_order[record["family"]], signal_bonus, record["skill"]),
            }
        )
    candidates.sort(key=lambda item: item["_sort"])
    for candidate in candidates:
        candidate.pop("_sort", None)
    capped: list[dict[str, Any]] = []
    seen_by_family: dict[str, int] = defaultdict(int)
    for candidate in candidates:
        family = candidate["family"]
        if seen_by_family[family] >= skill_limit:
            continue
        capped.append(candidate)
        seen_by_family[family] += 1
    return capped


def build_skill_bundles(
    family_candidates: list[dict[str, Any]],
    skill_candidates: list[dict[str, Any]],
    *,
    phase: str,
    skill_limit: int,
) -> list[dict[str, Any]]:
    skills_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for skill in skill_candidates:
        skills_by_family[skill["family"]].append(skill)

    bundles: list[dict[str, Any]] = []
    for family in family_candidates:
        bundles.append(
            {
                "phase": phase,
                "clan": family["clan"],
                "family": family["family"],
                "execution_owner": family["execution_owner"],
                "candidate_skills": [skill["skill"] for skill in skills_by_family.get(family["family"], [])[:skill_limit]],
                "boundary": family["boundary"],
                "exit_rule": "Load concrete SKILL.md only when the current phase needs it; drop this bundle after the phase or dispatch branch closes.",
            }
        )
    return bundles


def recall_capabilities(
    text: str,
    *,
    phase: str = "intake",
    office: str | None = None,
    semantic_keywords: list[str] | None = None,
    limit: int | None = None,
    registry_path: Path = DEFAULT_REGISTRY,
    clan_registry_path: Path = DEFAULT_CLAN_REGISTRY,
    inventory_path: Path = DEFAULT_INVENTORY,
    skill_limit: int = DEFAULT_SKILL_LIMIT,
) -> dict[str, Any]:
    registry = load_registry(registry_path)
    clan_registry = load_clan_registry(clan_registry_path)
    clan_lookup = load_clan_lookup(clan_registry_path)
    family_lookup = build_family_lookup(registry)
    max_family_candidates = int(limit or registry.get("max_candidates") or 3)
    max_clan_candidates = int(clan_registry.get("max_clan_candidates") or 2)
    normalized_semantic = normalize_semantic_keywords(semantic_keywords)

    clan_candidates: list[dict[str, Any]] = []
    for clan in clan_registry.get("clans", []):
        confidence, matched = score_clan(
            clan,
            text=text,
            semantic_keywords=normalized_semantic,
            family_lookup=family_lookup,
        )
        if confidence < 0.45:
            continue
        clan_candidates.append(
            {
                "clan": str(clan.get("clan", "")),
                "title": str(clan.get("title", "")),
                "confidence": round(confidence, 2),
                "reason": "matched clan signals: " + ", ".join(matched),
                "recall_owner": office or " / ".join({str(owner) for entry in registry["families"] for owner in entry.get("recall_owners", [])}),
                "execution_boundary": "clan is recall context only; execution remains family-bound",
                "families": [str(family) for family in clan.get("families", [])],
            }
        )
    clan_candidates.sort(key=lambda item: (-float(item["confidence"]), str(item["clan"])))
    clan_candidates = clan_candidates[:max_clan_candidates]
    selected_clans = {candidate["clan"] for candidate in clan_candidates}
    selected_families_by_clan = {candidate["clan"]: set(candidate["families"]) for candidate in clan_candidates}

    family_matches: list[dict[str, Any]] = []
    for entry in registry["families"]:
        family = entry["family"]
        clan = clan_lookup.get(family, "")
        if selected_clans and clan not in selected_clans:
            continue
        confidence, matched = score_entry(
            entry,
            text=text,
            semantic_keywords=normalized_semantic,
            phase=phase,
            office=office,
        )
        if confidence < 0.45:
            continue
        if selected_families_by_clan and family not in selected_families_by_clan.get(clan, set()):
            continue
        recall_owner = office if office in entry.get("recall_owners", []) else " / ".join(entry.get("recall_owners", []))
        reason = f"matched triggers: {', '.join(matched)}"
        if phase:
            reason += f"; phase={phase}"
        if office:
            reason += f"; office={office}"
        if normalized_semantic:
            reason += f"; semantic_keywords={', '.join(normalized_semantic)}"
        family_matches.append(
            {
                "family": family,
                "clan": clan,
                "confidence": round(confidence, 2),
                "reason": reason,
                "recall_owner": recall_owner,
                "execution_owner": entry["execution_owner"],
                "boundary": entry["boundary"],
            }
        )

    family_matches.sort(key=lambda item: (-float(item["confidence"]), str(item["family"])))
    family_candidates = family_matches[:max_family_candidates]
    selected_family_by_clan: dict[str, list[str]] = defaultdict(list)
    for candidate in family_candidates:
        selected_family_by_clan[candidate["clan"]].append(candidate["family"])
    for candidate in clan_candidates:
        retained = selected_family_by_clan.get(candidate["clan"])
        if retained:
            candidate["families"] = retained

    skill_candidates = build_skill_candidates(
        family_candidates,
        text=text,
        semantic_keywords=normalized_semantic,
        inventory_path=inventory_path,
        skill_limit=skill_limit,
    )
    skill_bundles = build_skill_bundles(
        family_candidates,
        skill_candidates,
        phase=phase,
        skill_limit=skill_limit,
    )

    return {
        "input": {
            "text": text,
            "phase": phase,
            "office": office or "",
            "semantic_keywords": normalized_semantic,
            "limit": max_family_candidates,
            "clan_limit": max_clan_candidates,
            "skill_limit": skill_limit,
        },
        "clan_candidates": clan_candidates,
        "family_candidates": family_candidates,
        "skill_candidates": skill_candidates,
        "skill_bundles": skill_bundles,
        "candidates": family_candidates,
        "policy": {
            "max_clan_candidates": max_clan_candidates,
            "max_family_candidates": max_family_candidates,
            "max_skills_per_family": skill_limit,
            "authority": "clan recall is context only; execution remains with 六部 under family allowlist.md and mapping.md",
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recall likely sxlb skill clans first, then family candidates.")
    parser.add_argument("--text", help="User task text. If omitted, stdin is used.")
    parser.add_argument("--phase", default="intake", help="Lifecycle phase, e.g. intake, planning, dispatch.")
    parser.add_argument("--office", help="Optional recalling office, e.g. 太子, 中书省, 尚书省.")
    parser.add_argument(
        "--semantic-keyword",
        action="append",
        default=[],
        help="Agent-derived normalized capability keyword. Repeatable; comma-separated values are also accepted.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Maximum candidates; defaults to registry max_candidates.")
    parser.add_argument("--skill-limit", type=int, default=DEFAULT_SKILL_LIMIT, help="Maximum concrete skill candidates per selected family.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    text = args.text if args.text is not None else sys.stdin.read()
    result = recall_capabilities(
        text,
        phase=args.phase,
        office=args.office,
        semantic_keywords=args.semantic_keyword,
        limit=args.limit,
        registry_path=args.registry,
        skill_limit=args.skill_limit,
    )
    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for candidate in result["clan_candidates"]:
            print(f"{candidate['clan']} {candidate['confidence']}: {candidate['reason']}")
        for candidate in result["family_candidates"]:
            print(f"{candidate['family']} {candidate['confidence']}: {candidate['reason']}")
        if not result["clan_candidates"] and not result["family_candidates"]:
            print("none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
