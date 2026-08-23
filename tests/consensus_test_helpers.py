from __future__ import annotations

import copy
from typing import Any

from openfs_runtime import stable_digest


def registry_bound_case(
    proposal: dict[str, Any], assessments: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bound = copy.deepcopy(assessments)
    agents = [
        {
            "agent_id": proposal["created_by_agent_id"],
            "enabled": True,
            "role": "discovery",
            "provider": "test-provider-author",
            "model_family": "test-model-author",
            "prompt_profile": "test-author-v1",
            "agent_independence_group": "test-author-group",
        }
    ]
    for assessment in bound:
        group = assessment["agent_independence_group"]
        role = "critic" if assessment["reviewer_agent_id"].startswith("critic") else "validator"
        agents.append(
            {
                "agent_id": assessment["reviewer_agent_id"],
                "enabled": True,
                "role": role,
                "provider": f"test-provider-{group}",
                "model_family": f"test-model-{group}",
                "prompt_profile": f"test-{role}-v1",
                "agent_independence_group": group,
            }
        )
    registry = {"schema_version": "0.1.0", "registry_status": "test", "agents": agents}
    digest = stable_digest(registry)
    by_id = {item["agent_id"]: item for item in agents}
    for assessment in bound:
        reviewer = by_id[assessment["reviewer_agent_id"]]
        assessment["reviewer_identity"] = {
            "provider": reviewer["provider"],
            "model_family": reviewer["model_family"],
            "prompt_profile": reviewer["prompt_profile"],
            "role": reviewer["role"],
        }
        assessment["agent_registry_digest"] = digest
    return registry, bound
