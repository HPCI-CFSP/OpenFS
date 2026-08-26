#!/usr/bin/env python3
"""Check bilingual completeness and recurring wording defects in public content."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = Path("knowledge/public")
READER_FACING_JSON = (
    Path("config/research-baseline.json"),
    Path("config/roadmap-portfolio.json"),
)
READER_FACING_JSON_GLOBS = ("roadmaps/scenarios/accepted/*.json",)
JAPANESE_TEXT = re.compile(r"[ぁ-んァ-ヶ一-龯]")
JAPANESE_SENTENCE_END = re.compile(r"[。！？]$")
ENGLISH_SENTENCE_END = re.compile(r"[.!?]$")
COMPLETE_SENTENCE_FIELDS = {
    "caveat",
    "condition",
    "current_state",
    "detail",
    "effect",
    "estimate_method",
    "hpci_implications",
    "hpci_relevance",
    "impact",
    "next_action",
    "note",
    "notice",
    "objective",
    "purpose",
    "rationale",
    "statement",
}

# These are reader-facing defects, not a general prohibition on English product
# names or OpenFS identifiers. Keep the list narrow enough to avoid rewriting
# official terminology mechanically.
BANNED_ALL = {
    "Github": "GitHub",
    "Independent-model Consensus": "Consensus review by independent models",
    "independent-model Consensus": "Consensus review by independent models",
    "capacity-memory": "high-capacity memory",
    "Eithernet": "Ethernet",
    "いづれ": "いずれ",
    "プロプラエタリ": "プロプライエタリ",
    "性能予測面": "性能予測",
    "情報の鮮度": "情報の更新状況",
    "調査元:": "出典:",
    "3nm SoIC": "3 nm SoIC",
    "200Gbps/lane": "200 Gbit/s per lane",
    "0.5x to 1.5x": "0.5 to 1.5 times",
}

BANNED_JA = {
    "Coverage Gap": "未確認事項",
    "独立Review": "独立レビュー",
    "Center Run": "センター調査実行",
    "HTTP監査run": "HTTP到達性監査",
    "Harness スキーマ": "ハーネスのスキーマ",
    "statusはopen": "状態は未解決",
    "生成fallback": "自動生成した検索案",
    "各Profile": "各センタープロファイル",
    "項目Profile": "項目からなるセンタープロファイル",
    "compile wrapper": "コンパイル用ラッパー",
    "major release": "メジャーリリース",
    "5.0 subset": "5.0の一部",
    "code移植": "コード移植",
    "同一code": "同一のソースコード",
    "hybrid 接合": "ハイブリッド接合",
    "workload適合": "ワークロード適合性",
    "science ベンチマーク": "科学ベンチマーク",
    "scheduler連携": "ジョブスケジューラーとの連携",
    "memory bandwidth": "メモリ帯域",
    "memory product": "メモリ製品",
    "移行cost": "移行コスト",
    "page配置": "ページ配置",
    "障害domain": "障害ドメイン",
    "中央管理された": "一元管理された",
    "システム整備計画案 3案比較": "3つのシステム整備計画案",
    "対応Framework": "対応フレームワーク",
    "package供給": "パッケージ供給",
    "package修理": "パッケージの修理",
    "stack歩留まり": "積層全体の歩留まり",
    "複数vendor": "複数ベンダー",
    "feature互換性": "機能互換性",
    "training・debug": "学習・デバッグ",
    "複数compiler": "複数コンパイラ",
    "correctness・性能": "計算結果の妥当性・性能",
    "ベンチマーク・Proxy": "ベンチマーク・プロキシ",
    "scale-up/scale-out": "スケールアップ／スケールアウト",
    "Wafer-scale・": "ウェハスケール・",
    "Consensus Gate（合意判定）": "合意判定（Consensus Gate）",
    "合意形成状況": "合意判定状況",
    "合意形成レビュー": "合意判定レビュー",
    "未解決の確認事項": "未確認事項",
    "情報起源グループ": "独立した情報源グループ",
    "同一EEAまたはProxy": "同一のEEAアプリケーションまたはプロキシ",
    "Ethernet スタック": "Ethernetスタック",
    "UET トランスポート": "UETトランスポート",
    "GPU スケールアップ": "GPUのスケールアップ",
    "スケールアウト CPO": "スケールアウトCPO",
    "CPU ツールチェーン": "CPU向けツールチェーン",
    "GPU ツールチェーン": "GPU向けツールチェーン",
    "アクセラレータ API": "アクセラレータAPI",
    "HIP ランタイム": "HIPランタイム",
    "LLVM ツールチェーン": "LLVMツールチェーン",
    "Tensor Core mode": "Tensor Coreの動作モード",
    "高速Fourier": "高速フーリエ",
    "Kokkos バックエンド": "Kokkosバックエンド",
    "native プログラミングモデル": "ネイティブなプログラミングモデル",
    "x86-64/Arm ホスト": "x86-64/Armホスト",
    "ダイ-to-wafer": "ダイ・ツー・ウェハ（D2W）",
    "GPU バックエンド": "GPUバックエンド",
    "OpenMP オフロード": "OpenMPオフロード",
    "未公表はGap": "未公表事項は未確認事項",
    "libfabric プロバイダー": "libfabricプロバイダー",
    "別NDA面": "別のNDA対応環境",
    "Vera Rubin プラットフォーム": "Vera Rubinプラットフォーム",
    "Arm サーバー": "Armサーバー",
    "代表アプリとProxy": "代表アプリケーションとプロキシアプリケーション",
    "厳密な依存再現": "依存関係まで含めた厳密な実行環境の再現",
    "初回スキャン": "初回調査",
    "未解消Gap": "解消されていない事項",
    "・Gap再評価": "と未確認事項の再評価",
    "後工程化": "設計後半にずれ込む",
    "長尾アプリ": "利用頻度が低い、または移植が難しいアプリケーション群",
    "公開面": "公開リポジトリや公開サイト",
    "性能電力比": "電力当たり性能",
    "実装追随": "各実装の対応状況",
    "単一モデル作業版": "単一のAIモデルが作成した作業版",
    "単一モデル暫定版": "単一のAIモデルが作成した暫定版",
    "専用データ 経路": "専用データ経路",
    "スケールアップ 通信": "スケールアップ通信",
    "信頼度の低い分析予測": "確度の低い、分析に基づく予測",
    "代表アプリケーションの正当性": "代表アプリケーションの計算結果の妥当性",
    "正当性・再現性・公開可能性": "計算結果の妥当性・再現性・公開可能性",
    "計算結果の正当性": "計算結果の妥当性",
    "結果正当性": "計算結果の妥当性",
    "センター別導入波": "センターごとの段階的な導入",
    "責任ある人の判断": "判断責任者による決定",
    "traffic benchmark": "トラフィック・ベンチマーク",
    "compiler・library": "コンパイラ・ライブラリ",
    "HPCI benchmark": "HPCI向けベンチマーク",
    "更新窓": "更新時期",
    "調達時の採点": "調達評価",
    "全国代表性": "全国規模での代表性",
    "圧縮接続": "圧接式の接続",
    "製品スタック": "ソフトウェアスタック",
    "閉ループ化": "自動的に反復する仕組み",
    "コンテナ/ワークフロー": "コンテナ、ワークフロー",
    "未移植アプリ": "未移植のアプリケーション",
    "次調達波": "次の調達機会",
    "公開暫定予測": "公開中の暫定予測",
    "EEA1アプリケーション暫定性能予測": "EEA1アプリケーションの暫定性能予測",
    "提供窓": "課題募集上の提供期間",
    "複数整備案v1": "システム整備計画案 v1",
    "新旧システム継続測定": "新旧システムの継続測定",
    "信頼度の低い相対性能予測": "確度の低い相対性能予測",
    "問題拡大型入力": "問題サイズを拡大した入力",
    "重複実行モデル": "計算・通信のオーバーラップを扱うモデル",
    "標準規模128ノード": "標準規模である128ノード",
    "疎行列・Allreduce": "疎行列演算とAllreduce",
    "調達テンプレート判断": "調達条件の策定",
    "共通データ面": "共通データプレーン",
    "標準ファブリックと光化": "標準ファブリックと光接続の段階導入",
    "自動昇格": "正式採用",
    "人の公開承認": "人による公開承認",
    "推奨順位ではありません": "推奨順位を示すものではありません",
    "プロファイル契約": "プロファイル必須項目",
    "OpenFS分析値": "OpenFSによる概算",
    "11の評価軸": "11項目の評価軸",
    "ソースコミット": "生成元コミット",
    "AI CPU": "AI向けCPU",
    "サーバーDDR": "サーバー向けDDR",
    "容量帯域比": "容量対帯域比",
    "CPU主記憶": "CPUに直結する主記憶",
    "調達テンプレート実証": "標準調達条件の実証",
    "分離必須": "別々に実施",
    "独立モデル": "独立したAIモデル",
    "単一モデル": "単一のAIモデル",
    "単一のモデル": "単一のAIモデル",
    "P0優先ロードマップ": "優先度P0のロードマップ",
    "根拠監査を開く": "根拠情報の監査を開く",
    "調査基準日時点": "調査基準日現在",
    "基準日時点": "調査基準日現在",
    "OpenFSの提案。": "OpenFSは〜を提案する。",
    "OpenFS提案。": "OpenFSは〜を提案する。",
    "公開済み。": "公開された。",
}

# Site source files contain both language dictionaries. Restrict checks there to
# phrases that are unambiguously Japanese or mixed-language defects.
BANNED_SITE_JA = {
    defect: replacement
    for defect, replacement in BANNED_JA.items()
    if defect
    in {
        "独立Review",
        "Center Run",
        "HTTP監査run",
        "Harness スキーマ",
        "statusはopen",
        "生成fallback",
        "各Profile",
        "項目Profile",
        "5.0 subset",
        "code移植",
        "同一code",
        "hybrid 接合",
        "workload適合",
        "science ベンチマーク",
        "scheduler連携",
        "memory bandwidth",
        "memory product",
        "移行cost",
        "page配置",
        "障害domain",
        "中央管理された",
        "システム整備計画案 3案比較",
        "ダイ-to-wafer",
        "GPU バックエンド",
        "OpenMP オフロード",
        "未公表はGap",
        "libfabric プロバイダー",
        "別NDA面",
        "Vera Rubin プラットフォーム",
        "Arm サーバー",
        "代表アプリとProxy",
        "厳密な依存再現",
        "初回スキャン",
        "人の公開承認",
        "推奨順位ではありません",
        "プロファイル契約",
        "OpenFS分析値",
        "11の評価軸",
        "ソースコミット",
        "分離必須",
        "独立モデル",
        "単一モデル",
        "単一のモデル",
        "P0優先ロードマップ",
        "根拠監査を開く",
        "調査基準日時点",
        "基準日時点",
        "OpenFSの提案。",
        "OpenFS提案。",
        "公開済み。",
    }
}
BANNED_SITE_JA.update(
    {
        "検証状態": "検証状況",
        "合意形成の候補": "合意判定の候補",
        "Consensus Gate（合意判定）": "合意判定（Consensus Gate）",
        "合意形成状況": "合意判定状況",
        "合意形成レビュー": "合意判定レビュー",
        "未解決の確認事項": "未確認事項",
        "· Consensus ${": "· ${tr(\"consensusStatus\")}: ${",
        '["Gap", tr(': '[tr("gapId"), tr(',
        "`contract ${": "`${tr(\"profileContract\")} ${",
        "} target rechecks`": '} ${tr("pastTargetRechecks")}`',
    }
)


def _walk(value: Any, location: str = "$") -> Iterator[tuple[str, Any]]:
    yield location, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{location}[{index}]")


def _validate_pair_values(
    value: dict[str, Any],
    location: str,
    left_key: str,
    right_key: str,
    errors: list[str],
) -> None:
    left = value[left_key]
    right = value[right_key]
    if type(left) is not type(right):
        errors.append(
            f"{location}.{left_key} and {right_key} use different value types"
        )
    elif isinstance(left, str) and (not left.strip() or not right.strip()):
        empty_key = left_key if not left.strip() else right_key
        errors.append(f"{location}.{empty_key} is empty")
    elif isinstance(left, list) and len(left) != len(right):
        errors.append(
            f"{location}.{left_key} and {right_key} have different item counts"
        )


def _validate_pairs(
    value: Any,
    location: str,
    errors: list[str],
    *,
    allow_legacy_japanese: bool = False,
) -> None:
    if isinstance(value, dict):
        keys = set(value)
        for key in sorted(keys):
            if key.endswith("_ja"):
                counterpart = f"{key[:-3]}_en"
                if counterpart not in keys:
                    errors.append(f"{location}.{key} has no {counterpart}")
                else:
                    _validate_pair_values(value, location, key, counterpart, errors)
            elif key.endswith("_en"):
                explicit_counterpart = f"{key[:-3]}_ja"
                if explicit_counterpart in keys:
                    # Explicit pairs are validated once from the `_ja` branch.
                    continue
                legacy_counterpart = key[:-3]
                counterpart = (
                    legacy_counterpart
                    if allow_legacy_japanese and legacy_counterpart in keys
                    else explicit_counterpart
                )
                if counterpart not in keys:
                    expected = (
                        f"{explicit_counterpart} or {legacy_counterpart}"
                        if allow_legacy_japanese
                        else explicit_counterpart
                    )
                    errors.append(f"{location}.{key} has no {expected}")
                else:
                    _validate_pair_values(value, location, counterpart, key, errors)
        for key, child in value.items():
            _validate_pairs(
                child,
                f"{location}.{key}",
                errors,
                allow_legacy_japanese=allow_legacy_japanese,
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_pairs(
                child,
                f"{location}[{index}]",
                errors,
                allow_legacy_japanese=allow_legacy_japanese,
            )


def _validate_wording(
    payload: Any, relative: Path, errors: list[str]
) -> None:
    for location, value in _walk(payload, str(relative)):
        if not isinstance(value, str):
            continue
        for defect, replacement in BANNED_ALL.items():
            if defect in value:
                errors.append(
                    f"{location}: use {replacement!r} instead of {defect!r}"
                )
        if JAPANESE_TEXT.search(value):
            for defect, replacement in BANNED_JA.items():
                if defect in value:
                    errors.append(
                        f"{location}: use {replacement!r} instead of {defect!r}"
                    )


def _validate_sentence_endings(
    value: Any,
    location: str,
    errors: list[str],
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str):
                if key.endswith("_ja") and key[:-3] in COMPLETE_SENTENCE_FIELDS:
                    if not JAPANESE_SENTENCE_END.search(child.strip()):
                        errors.append(
                            f"{location}.{key} must be a complete Japanese sentence"
                        )
                elif key.endswith("_en") and key[:-3] in COMPLETE_SENTENCE_FIELDS:
                    if not ENGLISH_SENTENCE_END.search(child.strip()):
                        errors.append(
                            f"{location}.{key} must be a complete English sentence"
                        )
                elif (
                    key in COMPLETE_SENTENCE_FIELDS
                    and f"{key}_en" in value
                    and JAPANESE_TEXT.search(child)
                    and not JAPANESE_SENTENCE_END.search(child.strip())
                ):
                    errors.append(
                        f"{location}.{key} must be a complete Japanese sentence"
                    )
            _validate_sentence_endings(child, f"{location}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_sentence_endings(child, f"{location}[{index}]", errors)


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    public_root = root / PUBLIC_ROOT
    if not public_root.exists():
        return [f"missing public-content directory: {PUBLIC_ROOT}"]

    for path in sorted(public_root.rglob("*.json")):
        relative = path.relative_to(root)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot read JSON: {exc}")
            continue
        _validate_pairs(payload, str(relative), errors)
        _validate_wording(payload, relative, errors)
        _validate_sentence_endings(payload, str(relative), errors)

    reader_facing_paths = [root / path for path in READER_FACING_JSON]
    for pattern in READER_FACING_JSON_GLOBS:
        reader_facing_paths.extend(sorted(root.glob(pattern)))
    for path in reader_facing_paths:
        if not path.exists():
            continue
        relative = path.relative_to(root)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot read JSON: {exc}")
            continue
        if relative.parts[:3] == ("roadmaps", "scenarios", "accepted"):
            _validate_pairs(
                payload,
                str(relative),
                errors,
                allow_legacy_japanese=True,
            )
        _validate_wording(payload, relative, errors)
        _validate_sentence_endings(payload, str(relative), errors)

    public_documents = [Path("README.md"), Path("README.ja.md")]
    site_root = root / "site"
    if site_root.exists():
        public_documents.extend(
            path.relative_to(root)
            for pattern in ("*.html", "*.js")
            for path in sorted(site_root.glob(pattern))
        )

    for relative in public_documents:
        path = root / relative
        if not path.exists():
            errors.append(f"missing public document: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for defect, replacement in BANNED_ALL.items():
            if defect in text:
                errors.append(
                    f"{relative}: use {replacement!r} instead of {defect!r}"
                )
        if relative == Path("README.ja.md") or relative.parts[0] == "site":
            defects = (
                BANNED_SITE_JA if relative.parts[0] == "site" else BANNED_JA
            )
            for defect, replacement in defects.items():
                if defect in text:
                    errors.append(
                        f"{relative}: use {replacement!r} instead of {defect!r}"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(f"public language error: {error}")
        return 1
    print("Public bilingual language checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
