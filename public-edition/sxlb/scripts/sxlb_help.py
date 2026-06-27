#!/usr/bin/env python3
"""Print a compact user-facing SXLB command guide."""

from __future__ import annotations

import argparse
import json
from typing import Any


COMMANDS: list[dict[str, str]] = [
    {
        "command": "继续",
        "action": "continue",
        "use_when": "让当前 SXLB 案件按已定方向继续推进。",
        "effect": "进入下一步执行、验证或回奏，不要求你选择内部架构。",
    },
    {
        "command": "暂停",
        "action": "pause",
        "use_when": "你想先停一下，避免我继续改文件或跑命令。",
        "effect": "保留当前状态，等待你的下一句指令。",
    },
    {
        "command": "体检",
        "action": "doctor",
        "use_when": "你不确定 SXLB 当前是不是正常、哪里坏了、外部能力是否可用。",
        "effect": "运行 doctor 思路的只读健康检查；也可直接执行 scripts/sxlb_doctor.py。",
    },
    {
        "command": "重审",
        "action": "review_again",
        "use_when": "你觉得计划、结论或完成声明不稳，需要再过一遍门下复核。",
        "effect": "回到复核视角，优先找风险、遗漏和未验证项。",
    },
    {
        "command": "事件簿",
        "action": "show_ledger",
        "use_when": "你想知道这个案子已经发生过哪些关键动作。",
        "effect": "查看或更新案卷里的事件记录。",
    },
    {
        "command": "侍讲官 <问题>",
        "action": "ask_officer",
        "use_when": "你想先听白话解释，而不是继续工程执行。",
        "effect": "用解释模式回答当前概念、改动、风险或下一步。",
    },
    {
        "command": "退朝",
        "action": "exit_court",
        "use_when": "本轮 SXLB 工作结束，准备收尾并退出 governed mode。",
        "effect": "进入退朝清算，完成必要记录和复核后退出。",
    },
]


def help_report() -> dict[str, Any]:
    return {
        "title": "SXLB 常用命令",
        "commands": COMMANDS,
        "doctor_command": "python3 $SXLB_HOME/scripts/sxlb_doctor.py",
    }


def render_human(report: dict[str, Any]) -> str:
    lines = [
        report["title"],
        "不知道该怎么推进时，优先用这些命令：",
        "",
    ]
    for item in report["commands"]:
        lines.append(f"- {item['command']}")
        lines.append(f"  什么时候用：{item['use_when']}")
        lines.append(f"  会发生什么：{item['effect']}")
    lines.extend([
        "",
        "体检脚本：",
        f"- {report['doctor_command']}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Print SXLB common command help.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    report = help_report()
    if args.json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
