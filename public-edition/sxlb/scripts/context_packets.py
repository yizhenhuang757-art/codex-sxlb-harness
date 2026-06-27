#!/usr/bin/env python3
"""Scaffold and validate lightweight sxlb context packet files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = ROOT / "templates"

PACKET_TEMPLATES = (
    "intake-context.md",
    "dispatch-packet.md",
    "review-grill.md",
)

REQUIRED_FIELDS = {
    "intake-context.md": (
        "案由",
        "用户目标",
        "约束",
        "上下文入口",
        "下一站",
        "关键未知",
        "不做什么",
    ),
    "dispatch-packet.md": (
        "官署",
        "任务",
        "readiness",
        "共享只读",
        "可写范围",
        "禁写范围",
        "回传物",
    ),
    "review-grill.md": (
        "来源",
        "假设检查",
        "复杂度检查",
        "边界检查",
        "验证标准检查",
    ),
}

INTAKE_FORBIDDEN_MARKERS = (
    "PRD：",
    "ADR：",
    "决策树：",
    "实现方案：",
    "canonical 决策：",
    "验收标准：",
)

DUPLICATE_FIELD_CHECKS = (
    ("intake-context.md", "case.md", "用户目标", "用户目标"),
    ("intake-context.md", "case.md", "约束", "约束"),
    ("intake-context.md", "case.md", "上下文入口", "上下文入口"),
    ("intake-context.md", "case.md", "下一站", "下一站"),
    ("intake-context.md", "case.md", "关键未知", "关键未知"),
    ("dispatch-packet.md", "dispatch-order.md", "官署", "官署"),
    ("dispatch-packet.md", "dispatch-order.md", "任务", "任务"),
    ("dispatch-packet.md", "dispatch-order.md", "共享只读", "共享只读"),
    ("dispatch-packet.md", "dispatch-order.md", "可写范围", "可写范围"),
    ("dispatch-packet.md", "dispatch-order.md", "禁写范围", "禁写范围"),
    ("dispatch-packet.md", "dispatch-order.md", "回传物", "回传物"),
    ("review-grill.md", "menxia-review.md", "来源", "来源"),
    ("review-grill.md", "menxia-review.md", "假设检查", "四问-假设检查"),
    ("review-grill.md", "menxia-review.md", "复杂度检查", "四问-复杂度检查"),
    ("review-grill.md", "menxia-review.md", "边界检查", "四问-改动边界检查"),
    ("review-grill.md", "menxia-review.md", "验证标准检查", "四问-验证方式检查"),
)

MIN_DUPLICATE_VALUE_CHARS = 20


def scaffold_context_packets(
    case_dir: Path,
    *,
    force: bool = False,
    templates: Iterable[str] = PACKET_TEMPLATES,
) -> list[str]:
    """Create context packet files from bundled templates."""
    case_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for name in templates:
        src = TEMPLATES_DIR / name
        dst = case_dir / name
        if not src.exists():
            raise FileNotFoundError(f"Missing context packet template: {src}")
        if dst.exists() and not force:
            continue
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        created.append(name)
    return created


def _field_present(text: str, field: str) -> bool:
    return f"- {field}：" in text or f"- {field}:" in text


def _field_value(text: str, field: str) -> str | None:
    for line in text.splitlines():
        for marker in (f"- {field}：", f"- {field}:"):
            if line.startswith(marker):
                return line[len(marker) :].strip()
    return None


def _normalized_value(value: str | None) -> str | None:
    if value is None or _is_empty_or_placeholder(value):
        return None
    normalized = " ".join(value.split())
    if len(normalized) < MIN_DUPLICATE_VALUE_CHARS:
        return None
    return normalized


def _is_empty_or_placeholder(value: str | None) -> bool:
    if value is None:
        return False
    if not value:
        return True
    if value in {"n/a", "none", "无"}:
        return False
    return value.startswith("<") and value.endswith(">")


def validate_context_packet(path: Path, packet_name: str | None = None) -> list[str]:
    """Return structural validation issues for one context packet."""
    packet = packet_name or path.name
    if packet not in REQUIRED_FIELDS:
        raise ValueError(f"Unknown context packet type: {packet}")
    if not path.exists():
        return [f"missing packet: {path}"]

    text = path.read_text(encoding="utf-8")
    issues: list[str] = []
    for field in REQUIRED_FIELDS[packet]:
        if not _field_present(text, field):
            issues.append(f"missing required field: {field}")
            continue
        if _is_empty_or_placeholder(_field_value(text, field)):
            issues.append(f"empty or placeholder field: {field}")

    if packet == "intake-context.md":
        forbidden = [marker for marker in INTAKE_FORBIDDEN_MARKERS if marker in text]
        if forbidden:
            issues.append(f"太子越权: intake-context contains planning/canonical markers {', '.join(forbidden)}")

    return issues


def find_duplicate_context_records(case_dir: Path) -> list[str]:
    """Return warnings when optional packets repeat substantive core fields verbatim."""
    cache: dict[str, str] = {}
    warnings: list[str] = []
    for packet_name, core_name, packet_field, core_field in DUPLICATE_FIELD_CHECKS:
        packet_path = case_dir / packet_name
        core_path = case_dir / core_name
        if not packet_path.exists() or not core_path.exists():
            continue
        packet_text = cache.setdefault(packet_name, packet_path.read_text(encoding="utf-8"))
        core_text = cache.setdefault(core_name, core_path.read_text(encoding="utf-8"))
        packet_value = _normalized_value(_field_value(packet_text, packet_field))
        core_value = _normalized_value(_field_value(core_text, core_field))
        if packet_value and packet_value == core_value:
            warnings.append(
                f"duplicate core record: {packet_name} duplicates {core_name} field {packet_field}"
            )
    return warnings


def validate_context_packets(
    case_dir: Path,
    templates: Iterable[str] = PACKET_TEMPLATES,
    *,
    check_duplicates: bool = False,
) -> list[str]:
    """Return all validation issues for the context packets in a case directory."""
    issues: list[str] = []
    for name in templates:
        packet_issues = validate_context_packet(case_dir / name, name)
        issues.extend(f"{name}: {issue}" for issue in packet_issues)
    if check_duplicates:
        issues.extend(find_duplicate_context_records(case_dir))
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold or validate sxlb context packets.")
    parser.add_argument("case_dir", type=Path, help="Target sxlb case directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing context packet files")
    parser.add_argument("--validate", action="store_true", help="Validate packets instead of scaffolding")
    parser.add_argument(
        "--check-duplicates",
        action="store_true",
        help="With --validate, also flag packet fields that repeat core case records verbatim",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.validate:
        issues = validate_context_packets(args.case_dir, check_duplicates=args.check_duplicates)
        if issues:
            for issue in issues:
                print(issue)
            return 1
        print("Context packets valid.")
        return 0

    created = scaffold_context_packets(args.case_dir, force=args.force)
    if created:
        print("Created:")
        for name in created:
            print(f"- {name}")
    else:
        print("No files created; context packets already existed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
