#!/usr/bin/env python3
"""Build a deterministic review queue for roadmap freshness and timing risks."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-freshness-audit.json"
TARGET_BASES = {"vendor-target", "project-target", "policy-target"}
OBSERVED_BASES = {"observed", "standard-release"}
QUARTER = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
REACHABILITY_LABELS_JA = {
    "blocked": "自動取得が拒否された状態",
    "error": "取得時にエラーが発生した状態",
    "redirected": "別のURLへ転送された状態",
    "unreachable": "到達できない状態",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def quarter_number(value: str | None) -> int | None:
    return int(value[1]) if value else None


def publication_period(source: dict[str, Any]) -> tuple[int, int] | None:
    published_at = source.get("published_at")
    if not published_at:
        return None
    published = date.fromisoformat(published_at)
    return published.year, QUARTER[published.month]


def attention(
    roadmap_id: str,
    object_type: str,
    object_id: str,
    severity: str,
    reason: str,
    reason_ja: str,
    reason_en: str,
    next_action_ja: str,
    next_action_en: str,
) -> dict[str, Any]:
    return {
        "roadmap_id": roadmap_id,
        "object_type": object_type,
        "object_id": object_id,
        "severity": severity,
        "reason": reason,
        "reason_ja": reason_ja,
        "reason_en": reason_en,
        "next_action_ja": next_action_ja,
        "next_action_en": next_action_en,
    }


def build(
    root: Path,
    generated_at: str | None = None,
    source_audit_path: Path | None = None,
) -> dict[str, Any]:
    roadmaps = [load_json(path) for path in sorted((root / "knowledge/public/roadmaps").glob("*.json"))]
    if not roadmaps:
        raise ValueError("no public roadmaps found")
    as_of_values = {roadmap["as_of"] for roadmap in roadmaps}
    as_of = max(date.fromisoformat(value) for value in as_of_values)
    current_quarter = QUARTER[as_of.month]
    source_audit = load_json(source_audit_path or root / "knowledge/public/audits/roadmap-source-audit.json")
    reachability = {
        (item["roadmap_id"], item["source_id"]): (
            "not-audited" if item.get("error_kind") == "not-audited" else item["status"])
        for item in source_audit["results"]
    }

    items: list[dict[str, Any]] = []
    roadmap_summaries: list[dict[str, Any]] = []
    total_milestones = 0
    total_generation_bands = 0
    total_sources = 0
    for roadmap in roadmaps:
        roadmap_items: list[dict[str, Any]] = []
        milestones = [milestone for lane in roadmap["lanes"] for milestone in lane["milestones"]]
        generation_bands = [
            band
            for track in roadmap.get("tracks", [])
            for band in track.get("generation_bands", [])
        ]
        source_registry = {source["source_id"]: source for source in roadmap["sources"]}
        total_milestones += len(milestones)
        total_generation_bands += len(generation_bands)
        total_sources += len(roadmap["sources"])
        key_source_ids = {
            source_id
            for milestone in milestones
            if milestone["comparison_priority"] == "key"
            for source_id in milestone["source_ids"]
        } | {
            source_id
            for band in generation_bands
            for source_id in band["source_ids"]
        }
        for milestone in milestones:
            year = milestone["year"]
            quarter = quarter_number(milestone["quarter"])
            basis = milestone["timing_basis"]
            if basis == "no-public-date":
                roadmap_items.append(attention(
                    roadmap["roadmap_id"], "milestone", milestone["milestone_id"],
                    "high" if milestone["comparison_priority"] == "key" else "medium",
                    "no-public-date",
                    "公開された時期を確認できず、空欄を推測で補っていない。",
                    "No public date was confirmed; the timeline remains blank rather than inferred.",
                    "公式プロジェクト、標準化団体、ベンダーの発表を次回の調査で再検索する。",
                    "Recheck official project, standards, and vendor announcements in the next loop.",
                ))
            if basis in TARGET_BASES and year is not None:
                target_passed = year < as_of.year or (
                    year == as_of.year
                    and milestone["timing_precision"] == "quarter"
                    and quarter is not None
                    and quarter < current_quarter
                )
                if target_passed:
                    roadmap_items.append(attention(
                        roadmap["roadmap_id"], "milestone", milestone["milestone_id"], "high",
                        "target-date-passed",
                        "公開目標時期を過ぎているため、達成・延期・中止を一次情報で再確認する必要がある。",
                        "The public target date has passed and needs primary-source confirmation of completion, delay, or cancellation.",
                        "目標を実績へ自動変換せず、公式更新を確認して状態を改訂する。",
                        "Do not convert the target into an observed event; check official updates and revise its state.",
                    ))
            if basis in OBSERVED_BASES and year is not None:
                event_in_future = year > as_of.year or (
                    year == as_of.year and quarter is not None and quarter > current_quarter
                )
                if event_in_future:
                    roadmap_items.append(attention(
                        roadmap["roadmap_id"], "milestone", milestone["milestone_id"], "critical",
                        "future-observed-conflict",
                        "実績として分類された時期が基準日より後で、時制が矛盾している。",
                        "The event is classified as observed but dated after the audit baseline.",
                        "公開を停止し、日付または時期分類を一次情報に照らして修正する。",
                        "Block publication and correct the date or timing_basis against the primary source.",
                    ))
                if milestone["timing_precision"] == "quarter" and quarter is not None:
                    publication_periods = [
                        period
                        for source_id in milestone["source_ids"]
                        if (period := publication_period(source_registry[source_id])) is not None
                    ]
                    if publication_periods and all(
                        period > (year, quarter) for period in publication_periods
                    ):
                        roadmap_items.append(attention(
                            roadmap["roadmap_id"], "milestone", milestone["milestone_id"], "low",
                            "retrospective-source-timing-check",
                            "引用一次資料の公開四半期が、記録された実績四半期より後である。遡及報告は正当な場合があるが、出来事の時期を示す本文の確認が必要。",
                            "The cited primary sources were published after the recorded event quarter. Retrospective reporting may be valid, but the text must explicitly entail the event timing.",
                            "独立レビューで一次資料の本文を確認し、公開日を出来事の日付として代用しない。",
                            "Verify the primary-source text during independent review; do not substitute publication date for event date.",
                        ))
        for band in generation_bands:
            if band["timing_basis"] not in TARGET_BASES or band["end"] is None:
                continue
            end = band["end"]
            end_quarter = quarter_number(end["quarter"])
            if end["precision"] == "half-year":
                end_quarter = 2 if end["half"] == "H1" else 4
            elif end["precision"] == "year":
                end_quarter = 4
            target_passed = end["year"] < as_of.year or (
                end["year"] == as_of.year
                and end_quarter is not None
                and end_quarter < current_quarter
            )
            if target_passed:
                roadmap_items.append(attention(
                    roadmap["roadmap_id"], "generation-band", band["generation_band_id"], "high",
                    "generation-window-passed",
                    "世代見通しの公表目標窓を過ぎているため、標準化・製品化・延期を一次情報で再確認する必要がある。",
                    "The published target window in the generation outlook has passed and needs primary-source confirmation of standardization, product introduction, or delay.",
                    "世代区分を実績扱いへ自動変換せず、公式情報の更新を確認して境界、確度、未確認事項を改訂する。",
                    "Do not convert the band into an observed result; check official updates and revise boundaries, confidence, and gaps.",
                ))
        for source in roadmap["sources"]:
            if "published_at" not in source:
                roadmap_items.append(attention(
                    roadmap["roadmap_id"], "source", source["source_id"], "low",
                    "source-publication-date-unrecorded",
                    "情報源の公開日が構造化されておらず、更新状況を自動確認できない。",
                    "The source publication date is not recorded, so freshness cannot be assessed automatically.",
                    "ページ履歴または文書メタデータから日付を確認し、推測できなければ未記録のまま残す。",
                    "Check page history or document metadata and leave it unrecorded if no date can be established.",
                ))
            status = reachability.get((roadmap["roadmap_id"], source["source_id"]))
            if status == "not-audited":
                roadmap_items.append(attention(
                    roadmap["roadmap_id"], "source", source["source_id"], "medium",
                    "source-not-audited",
                    "このURLのHTTP到達性監査は未実施です。接続失敗や資料の誤りを意味しません。",
                    "HTTP reachability has not been audited for this URL. This is not a failed connection or a finding of error.",
                    "実行環境の権限を確認後に匿名HTTP監査を行う。管理されたWebツールによる内容確認と独立検証は別に記録する。",
                    "Audit anonymously only after execution authorization is verified. Record managed-Web content review and independent validation separately.",
                ))
            elif status and status != "reachable":
                roadmap_items.append(attention(
                    roadmap["roadmap_id"], "source", source["source_id"],
                    "high" if source["source_id"] in key_source_ids else "medium",
                    f"source-{status}",
                    f"到達性監査では、この情報源を{REACHABILITY_LABELS_JA.get(status, '要確認の状態')}と判定した。内容が誤っていることを意味しない。",
                    f"The reachability audit classified this source as {status}; this does not establish that its content is wrong.",
                    "公式の代替URLまたはアーカイブを探し、主張内容は独立に検証する。",
                    "Find an official alternate URL or archive and verify the claim independently.",
                ))
        counts = Counter(item["severity"] for item in roadmap_items)
        roadmap_summaries.append({
            "roadmap_id": roadmap["roadmap_id"],
            "milestone_count": len(milestones),
            "generation_band_count": len(generation_bands),
            "source_count": len(roadmap["sources"]),
            "attention_count": len(roadmap_items),
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
        })
        items.extend(roadmap_items)

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    items.sort(key=lambda item: (severity_order[item["severity"]], item["roadmap_id"], item["object_type"], item["object_id"], item["reason"]))
    for index, item in enumerate(items, 1):
        item["attention_id"] = f"RFAI-{index:04d}"
    counts = Counter(item["severity"] for item in items)
    reasons = Counter(item["reason"] for item in items)
    generated = generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-FRESHNESS-AUDIT-001",
        "status": "published",
        "audit_id": f"RFA-{as_of.strftime('%Y%m%d')}-001",
        "as_of": as_of.isoformat(),
        "generated_at": generated,
        "method_ja": "6本のロードマップを機械的に走査し、世代区分、時期未公表の項目、期限を過ぎた目標、基準日より後の実績、遡及報告、公開日が未記録の情報源、到達性の警告を、次回確認すべき項目として分類しました。",
        "method_en": "This audit mechanically scans six roadmaps and identifies items that require follow-up: generation bands, undated milestones, passed targets, observed events dated after the audit baseline, retrospective reports, sources without recorded publication dates, and reachability warnings.",
        "caveat_ja": "更新確認が必要という表示は、内容が誤っているという判定ではありません。過去の一次資料や遡及報告が現在も有効な場合があり、目標時期を過ぎただけでは、達成、延期、中止のいずれとも推定しません。",
        "caveat_en": "Freshness attention is not a finding of error. Older primary sources and retrospective reports may remain valid, and a passed target is not inferred to be completed, delayed, or cancelled.",
        "summary": {
            "roadmap_count": len(roadmaps),
            "milestone_count": total_milestones,
            "generation_band_count": total_generation_bands,
            "source_count": total_sources,
            "attention_count": len(items),
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
            "no_public_date_milestones": reasons["no-public-date"],
            "past_target_rechecks": reasons["target-date-passed"],
            "past_generation_window_rechecks": reasons["generation-window-passed"],
            "future_observed_conflicts": reasons["future-observed-conflict"],
            "retrospective_timing_checks": reasons["retrospective-source-timing-check"],
            "source_date_unknown": reasons["source-publication-date-unrecorded"],
            "source_attention": sum(count for reason, count in reasons.items() if reason.startswith("source-") and reason != "source-publication-date-unrecorded"),
        },
        "roadmap_summaries": roadmap_summaries,
        "attention_items": items,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-005",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at")
    parser.add_argument("--source-audit", type=Path)
    args = parser.parse_args()
    result = build(args.root, args.generated_at, args.source_audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
