#!/usr/bin/env python3
"""Validate a provider Worker result before updating trusted Run control state."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from openfs_runtime import manifest_control_digest, read_json, sha256_file, stable_digest
from run_controller import complete_work_item, fail_work_item


ROOT = Path(__file__).resolve().parents[1]


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Worker result timestamp must include a timezone")
    return parsed


def _repository_path(root: Path, ref: str) -> Path:
    relative = PurePosixPath(ref)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Worker reference must be repository-relative: {ref}")
    return root.joinpath(*relative.parts)


def _validate_contracts(root: Path, refs: list[str]) -> None:
    from jsonschema import Draft202012Validator, FormatChecker
    from validate_json_schemas import contract_schema, schema_registry

    schemas, registry = schema_registry(root)
    errors: list[str] = []
    for ref in refs:
        path = _repository_path(root, ref)
        payload = read_json(path)
        schema_name = contract_schema(path, root, payload)
        if schema_name is None:
            errors.append(f"no artifact contract is mapped for {ref}")
            continue
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        for error in validator.iter_errors(payload):
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            errors.append(f"{ref} [{schema_name}] {location}: {error.message}")
    if errors:
        raise ValueError("Worker artifact contract validation failed: " + "; ".join(errors))


def validate_output_identity(
    invocation: dict[str, Any], outputs: list[dict[str, Any]]
) -> None:
    role = invocation["role"]
    for output in outputs:
        if output.get("run_id") != invocation["run_id"]:
            raise ValueError("Worker output belongs to a different Run")
        if output.get("work_item_id") != invocation["work_item_id"]:
            raise ValueError("Worker output belongs to a different Work Item")
        artifact_time = output.get("reviewed_at") or output.get("created_at")
        if not isinstance(artifact_time, str) or not (
            _instant(invocation["prepared_at"])
            <= _instant(artifact_time)
            <= _instant(invocation["constraints"]["lease_expires_at"])
        ):
            raise ValueError("Worker output timestamp falls outside its invocation lease")
        if role in {"validator", "critic"}:
            if output.get("reviewer_agent_id") != invocation["agent_id"]:
                raise ValueError("Worker Assessment belongs to a different reviewer")
            expected = invocation["provider_binding"]
            identity = output.get("reviewer_identity", {})
            for key in ("provider", "model_family", "prompt_profile", "role"):
                if identity.get(key) != expected.get(key, role):
                    raise ValueError("Worker Assessment reviewer identity differs")
        elif output.get("created_by_agent_id") != invocation["agent_id"]:
            raise ValueError("Worker output belongs to a different creating Agent")


def validate_result(
    root: Path, invocation: dict[str, Any], result: dict[str, Any]
) -> None:
    if not re.fullmatch(r"WINV-[0-9A-F]{16}", str(invocation.get("invocation_id", ""))):
        raise ValueError("Worker invocation ID is invalid")
    if not re.fullmatch(r"WRES-[0-9A-F]{16}", str(result.get("result_id", ""))):
        raise ValueError("Worker result ID is invalid")
    invocation_payload = dict(invocation)
    invocation_digest = invocation_payload.pop("invocation_digest", None)
    if invocation_digest != stable_digest(invocation_payload):
        raise ValueError("Worker invocation digest differs")
    result_payload = dict(result)
    result_digest = result_payload.pop("result_digest", None)
    if result_digest != stable_digest(result_payload):
        raise ValueError("Worker result digest differs")
    if (
        result.get("invocation_id") != invocation.get("invocation_id")
        or result.get("invocation_digest") != invocation_digest
        or result.get("agent_id") != invocation.get("agent_id")
    ):
        raise ValueError("Worker result does not match its invocation")
    binding = invocation["provider_binding"]
    provider = result.get("provider", {})
    if (
        provider.get("provider") != binding["provider"]
        or provider.get("model_family") != binding["model_family"]
    ):
        raise ValueError("Worker result provider binding differs")
    if not (
        _instant(invocation["prepared_at"])
        <= _instant(result["completed_at"])
        <= _instant(invocation["constraints"]["lease_expires_at"])
    ):
        raise ValueError("Worker result falls outside the leased execution window")

    provenance = invocation["provenance"]
    expected_work_ref = (
        f"queue/{invocation['run_id']}/{invocation['work_item_id']}.json"
    )
    if provenance.get("work_item_ref") != expected_work_ref:
        raise ValueError("Worker invocation Work Item reference differs")
    work_item = read_json(_repository_path(root, expected_work_ref))
    if stable_digest(work_item) != provenance.get("work_item_digest"):
        raise ValueError("leased Work Item changed after invocation preparation")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != result["agent_id"]:
        raise RuntimeError("Worker result is not owned by the current lease holder")
    if work_item.get("output_paths") != invocation["constraints"]["output_paths"]:
        raise ValueError("Worker invocation output paths differ from the Work Item")
    manifest_ref = provenance["manifest_ref"]
    if manifest_ref != f"runs/{invocation['run_id']}/manifest.json":
        raise ValueError("Worker invocation Run manifest reference differs")
    manifest = read_json(_repository_path(root, manifest_ref))
    if manifest.get("status") not in {"created", "running"}:
        raise RuntimeError("Worker result requires a non-terminal Run")
    if manifest_control_digest(manifest) != provenance["manifest_control_digest"]:
        raise ValueError("pinned Run controls changed after invocation preparation")
    for ref_key, digest_key in (
        ("agent_registry_ref", "agent_registry_digest"),
        ("role_permissions_ref", "role_permissions_digest"),
    ):
        ref = provenance[ref_key]
        if stable_digest(read_json(_repository_path(root, ref))) != provenance[digest_key]:
            raise ValueError(f"pinned Worker configuration changed: {ref}")
    skill = invocation["skill"]
    skill_path = _repository_path(root, skill["snapshot_ref"])
    if not skill_path.is_file() or sha256_file(skill_path) != skill["digest"]:
        raise ValueError("pinned Worker Skill changed after invocation preparation")

    if result.get("status") == "completed":
        expected_refs = invocation["constraints"]["output_paths"]
        if result.get("output_refs") != expected_refs:
            raise ValueError("Worker result output set differs from its invocation")
        digests = result.get("output_digests", {})
        if set(digests) != set(expected_refs):
            raise ValueError("Worker result output digest keys differ")
        for ref in expected_refs:
            path = _repository_path(root, ref)
            if not path.is_file() or sha256_file(path) != digests[ref]:
                raise ValueError(f"Worker output is missing or changed: {ref}")
        usage = result.get("usage", {})
        if not isinstance(usage, dict) or not usage.get("measurement_note"):
            raise ValueError("Worker result requires a usage measurement note")
        for key in ("input_tokens", "output_tokens"):
            value = usage.get(key)
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value < 0
            ):
                raise ValueError(f"Worker result {key} is invalid")
        cost = usage.get("cost_usd")
        if cost is not None and (
            not isinstance(cost, (int, float))
            or isinstance(cost, bool)
            or cost < 0
        ):
            raise ValueError("Worker result cost_usd is invalid")
    elif result.get("status") == "failed":
        error = result.get("error", {})
        if (
            not isinstance(error.get("kind"), str)
            or not error["kind"].strip()
            or not isinstance(error.get("message"), str)
            or not error["message"].strip()
            or not isinstance(error.get("retryable"), bool)
        ):
            raise ValueError("failed Worker result requires an error")
    else:
        raise ValueError("Worker result status is invalid")


def accept(
    root: Path, *, invocation_ref: str, result_ref: str
) -> dict[str, Any]:
    invocation = read_json(_repository_path(root, invocation_ref))
    result = read_json(_repository_path(root, result_ref))
    validate_result(root, invocation, result)
    _validate_contracts(
        root,
        [invocation_ref, result_ref, *result.get("output_refs", [])],
    )
    validate_output_identity(
        invocation,
        [read_json(_repository_path(root, ref)) for ref in result.get("output_refs", [])],
    )
    now = _instant(result["completed_at"])
    common = {
        "root": root,
        "run_id": invocation["run_id"],
        "work_item_id": invocation["work_item_id"],
        "agent_id": invocation["agent_id"],
        "now": now,
    }
    if result["status"] == "completed":
        return complete_work_item(
            **common,
            output_refs=result["output_refs"],
            usage=result["usage"],
            worker_execution={
                "invocation_ref": invocation_ref,
                "invocation_digest": invocation["invocation_digest"],
                "result_ref": result_ref,
                "result_digest": result["result_digest"],
                "provider": result["provider"]["provider"],
                "model_family": result["provider"]["model_family"],
                "resolved_model_version": result["provider"]["resolved_model_version"],
                "request_id_digest": result["provider"]["request_id_digest"],
            },
        )
    error = result["error"]
    return fail_work_item(
        **common,
        error_kind=error["kind"],
        error_message=error["message"],
        retryable=error["retryable"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--invocation-ref", required=True)
    parser.add_argument("--result-ref", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    item = accept(
        args.root,
        invocation_ref=args.invocation_ref,
        result_ref=args.result_ref,
    )
    print(json.dumps({"work_item_id": item["work_item_id"], "status": item["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
