"""Apply the 4 famous trading laws (Murphy / Kidlin / Wilson / Gilbert) to setups.

These checks are deliberately deterministic and pure-Python so they run before
any LLM call — they form the "trade memory" filter described in
``knowledge/trading_laws.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from smc_core.setup import RRSetup

LawName = Literal["murphy", "kidlin", "wilson", "gilbert"]


@dataclass
class LawCheck:
    """Result of running the 4 laws against a setup."""

    setup_index: int  # position of the setup in the input list
    pass_all: bool
    severity: Literal["ok", "caution", "reject"]
    violations: list[tuple[LawName, str]] = field(default_factory=list)
    warnings: list[tuple[LawName, str]] = field(default_factory=list)
    lessons_passed: list[str] = field(default_factory=list)
    lessons_failed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "setup_index": self.setup_index,
            "pass_all": self.pass_all,
            "severity": self.severity,
            "violations": [{"law": name, "reason": reason} for name, reason in self.violations],
            "warnings": [{"law": name, "reason": reason} for name, reason in self.warnings],
            "lessons_passed": list(self.lessons_passed),
            "lessons_failed": list(self.lessons_failed),
        }


def _check_murphy(setup: RRSetup) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    warnings: list[str] = []

    if setup.stop_loss is None or setup.entry is None:
        violations.append("Setup thiếu SL hoặc entry — vi phạm 'SL kỷ luật'.")
        return violations, warnings

    risk = setup.risk_per_unit
    if risk <= 0:
        violations.append("Khoảng cách entry → SL bằng 0; setup không hợp lệ.")
        return violations, warnings

    risk_pct = risk / max(abs(setup.entry), 1e-9)
    if risk_pct < 5e-4:  # < 0.05%
        warnings.append(f"SL quá sát (risk = {risk_pct * 100:.4f}% giá) — fakeout risk cao.")

    if setup.rr_ratio < 3.0:
        violations.append(f"RR = {setup.rr_ratio:.2f} < 3.0 — vi phạm yêu cầu tối thiểu 1:3.")

    return violations, warnings


def _check_kidlin(setup: RRSetup) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    warnings: list[str] = []

    required_keywords = ("BOS", "IDM", "Order Block")
    notes_blob = " | ".join(setup.notes)
    missing = [kw for kw in required_keywords if kw not in notes_blob]
    if missing:
        violations.append(f"Notes thiếu các bước: {', '.join(missing)} — kế hoạch chưa rõ ràng.")

    if len(setup.notes) < 3:
        violations.append(f"Chỉ có {len(setup.notes)} notes; tối thiểu 3 bước (BOS / IDM / OB).")

    if setup.overlapping_fvg is None:
        warnings.append("Không có FVG overlap — confluence yếu hơn (vẫn chấp nhận được).")

    return violations, warnings


def _check_wilson(setup: RRSetup) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    warnings: list[str] = []

    has_reasoning = any(
        kw in note
        for note in setup.notes
        for kw in ("BOS", "CHoCH", "phá", "broke", "swept", "quét")
    )
    if not has_reasoning:
        violations.append(
            "Notes không giải thích được lý do cấu trúc hợp lệ — agent phải trình bày."
        )

    return violations, warnings


def _check_gilbert(setup: RRSetup) -> tuple[list[str], list[str]]:
    violations: list[str] = []
    warnings: list[str] = []

    if setup.entry == setup.stop_loss == setup.take_profit:
        violations.append("Entry/SL/TP trùng nhau — agent đang 'ép' tín hiệu, không hợp lệ.")

    return violations, warnings


def apply_trading_laws(setups: list[RRSetup]) -> list[LawCheck]:
    """Run the 4-law filter on each setup. Returns one LawCheck per input setup."""
    results: list[LawCheck] = []

    for i, setup in enumerate(setups):
        all_violations: list[tuple[LawName, str]] = []
        all_warnings: list[tuple[LawName, str]] = []

        for law, fn in (
            ("murphy", _check_murphy),
            ("kidlin", _check_kidlin),
            ("wilson", _check_wilson),
            ("gilbert", _check_gilbert),
        ):
            v, w = fn(setup)
            all_violations.extend((law, msg) for msg in v)
            all_warnings.extend((law, msg) for msg in w)

        # 4 trader lessons (post-filter checklist).
        lessons_passed: list[str] = []
        lessons_failed: list[str] = []

        if setup.rr_ratio >= 3.0 and setup.stop_loss is not None:
            lessons_passed.append("hieu_ro_tam_ly")
        else:
            lessons_failed.append("hieu_ro_tam_ly")

        if len(setup.notes) >= 3:
            lessons_passed.append("ghi_chep_ro_rang")
        else:
            lessons_failed.append("ghi_chep_ro_rang")

        if any("BOS" in n or "CHoCH" in n for n in setup.notes):
            lessons_passed.append("dau_tu_kien_thuc")
        else:
            lessons_failed.append("dau_tu_kien_thuc")

        if not all_violations:
            lessons_passed.append("chiu_trach_nhiem")
        else:
            lessons_failed.append("chiu_trach_nhiem")

        if all_violations:
            severity: Literal["ok", "caution", "reject"] = "reject"
        elif all_warnings or lessons_failed:
            severity = "caution"
        else:
            severity = "ok"

        results.append(
            LawCheck(
                setup_index=i,
                pass_all=len(all_violations) == 0,
                severity=severity,
                violations=all_violations,
                warnings=all_warnings,
                lessons_passed=lessons_passed,
                lessons_failed=lessons_failed,
            )
        )

    return results
