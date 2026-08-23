#!/usr/bin/env python3
"""Build the public OpenFS GitHub Pages site from approved repository paths."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def public_projection(
    artifact: dict[str, Any],
    fields: list[str],
    required_metadata: dict[str, Any],
    required_bilingual_fields: list[str],
    approved_directives: dict[str, set[str]],
    label: str,
) -> dict[str, Any]:
    publication = artifact.get("publication")
    if not isinstance(publication, dict):
        raise ValueError(f"{label} has no publication metadata")
    for key, expected in required_metadata.items():
        if publication.get(key) != expected:
            raise ValueError(f"{label} has invalid publication metadata: {key}")
    if not publication.get("publication_decision_id"):
        raise ValueError(f"{label} has no publication decision")
    directive_id = publication.get("human_approval_directive_id")
    artifact_id = artifact.get("scenario_id") or artifact.get("report_id")
    if not directive_id or artifact_id not in approved_directives.get(directive_id, set()):
        raise ValueError(f"{label} has no matching human publication Directive")
    missing_languages = [key for key in required_bilingual_fields if not artifact.get(key)]
    if missing_languages:
        raise ValueError(f"{label} lacks bilingual fields: {missing_languages}")
    return {key: artifact[key] for key in fields if key in artifact}


def approved_publication_directives(root: Path, policy: dict[str, Any]) -> dict[str, set[str]]:
    allowed_statuses = set(policy["human_publication_directive_statuses"])
    approvals: dict[str, set[str]] = {}
    for path in sorted(root.glob(policy["human_publication_directive_glob"])):
        directive = load_json(path)
        if directive.get("directive_type") != "publication-approval":
            continue
        if directive.get("status") not in allowed_statuses:
            continue
        if not directive.get("submitted_by") or not directive.get("submitted_at"):
            continue
        approvals[directive["directive_id"]] = set(directive.get("publication_targets", []))
    return approvals


def collect_scenarios(root: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    allowed = set(policy["accepted_scenario_statuses"])
    directives = approved_publication_directives(root, policy)
    scenarios: list[dict[str, Any]] = []
    for path in sorted(root.glob(policy["accepted_scenario_glob"])):
        payload = load_json(path)
        candidates = payload.get("scenarios", [payload]) if isinstance(payload, dict) else []
        for scenario in candidates:
            status = scenario.get("status")
            if status not in allowed:
                raise ValueError(f"non-publishable scenario in accepted path: {path}: {status}")
            scenarios.append(
                public_projection(
                    scenario,
                    policy["scenario_public_fields"],
                    policy["required_publication_metadata"],
                    policy["scenario_required_bilingual_fields"],
                    directives,
                    f"scenario {scenario.get('scenario_id', path.name)}",
                )
            )
    return scenarios


def collect_reports(root: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    index_path = root / policy["report_index"]
    if not index_path.exists():
        return []
    allowed = set(policy["accepted_report_statuses"])
    directives = approved_publication_directives(root, policy)
    reports = load_json(index_path).get("reports", [])
    projected_reports = []
    for report in reports:
        if report.get("status") not in allowed:
            raise ValueError(
                f"non-publishable report in public index: {report.get('report_id')}"
            )
        projected_reports.append(
            public_projection(
                report,
                policy["report_public_fields"],
                policy["required_publication_metadata"],
                policy["report_required_bilingual_fields"],
                directives,
                f"report {report.get('report_id', 'unknown')}",
            )
        )
    return projected_reports


def build_public_data(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    baseline = load_json(root / policy["included_catalog"])
    i18n = load_json(root / policy["included_i18n"])
    technology_scope = load_json(root / "config" / "global-technology-scope.json")
    initial_ids = set(baseline["initial_catalog"]["topic_ids"])
    public_title_overrides_ja = i18n.get("topic_title_overrides_ja", {})
    topics = []
    for topic in baseline["topics"]:
        topics.append(
            {
                "topic_id": topic["topic_id"],
                "domain": topic["domain"],
                "title_ja": public_title_overrides_ja.get(
                    topic["topic_id"], topic["title_ja"]
                ),
                "title_en": i18n["topic_titles_en"][topic["topic_id"]],
                "status": topic["status"],
                "review_cadence": topic["review_cadence"],
                "catalog_origin": (
                    "protected-initial"
                    if topic["topic_id"] in initial_ids
                    else topic.get("catalog_origin", "human-directive")
                ),
            }
        )

    scenarios = collect_scenarios(root, policy)
    reports = collect_reports(root, policy)
    official_sources = [
        source for source in baseline["source_corpus"]
        if source.get("availability") == "registered-public-url"
    ]
    return {
        "schema_version": "0.1.0",
        "as_of": baseline["derived_at"],
        "baseline": {
            "baseline_id": baseline["baseline_id"],
            "catalog_revision": baseline["catalog_revision"],
            "topic_count": len(topics),
            "protected_initial_count": len(initial_ids),
            "official_source_count": len(official_sources),
            "complete": baseline["complete"],
            "open_gap_ids": baseline["open_gap_ids"],
        },
        "topics": topics,
        "technology_landscape": {
            "categories": [
                {"ja": ja, "en": en}
                for ja, en in zip(
                    i18n["technology_landscape"]["technology_categories_ja"],
                    technology_scope["technology_categories"],
                    strict=True,
                )
            ],
        },
        "scenarios": scenarios,
        "reports": reports,
        "publication": {
            "policy_id": policy["policy_id"],
            "information_plane": policy["information_plane"],
            "license_status": policy["license_status"],
            "license": policy["license"],
            "repository_url": "https://github.com/HPCI-CFSP/OpenFS",
        },
    }


def build(root: Path, output: Path) -> dict[str, Any]:
    policy = load_json(root / "config" / "publication-policy.json")
    source = root / policy["site_source"]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for filename in ("index.html", "styles.css", "app.js"):
        shutil.copy2(source / filename, output / filename)
    data_dir = output / "data"
    data_dir.mkdir()
    public_data = build_public_data(root, policy)
    serialized = json.dumps(public_data, ensure_ascii=False, separators=(",", ":"))
    (data_dir / "openfs-public.js").write_text(
        f"window.OPENFS_PUBLIC_DATA={serialized};\n", encoding="utf-8"
    )
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return public_data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    result = build(ROOT, args.output)
    print(
        f"Built OpenFS Pages: topics={len(result['topics'])}, "
        f"scenarios={len(result['scenarios'])}, reports={len(result['reports'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
