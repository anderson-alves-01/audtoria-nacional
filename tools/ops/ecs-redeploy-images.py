"""Register ECS task definitions with image tags and PUBLIC_OPEN UI bootstrap env."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

REGION = "sa-east-1"
CLUSTER = "sirta-prod"
API_IMAGE = "332380491162.dkr.ecr.sa-east-1.amazonaws.com/sirta-prod-api:0.3.101"
WEB_IMAGE = "332380491162.dkr.ecr.sa-east-1.amazonaws.com/sirta-prod-web:0.3.101"

API_ENV = [
    {"name": "SIRTA_ENV", "value": "prod"},
    {"name": "S3_BUCKET", "value": "sirta-prod-landing"},
    {"name": "OIDC_JWKS_PATH", "value": "/app/var/oidc/jwks.json"},
    {"name": "OIDC_SIGNING_KEY_PATH", "value": "/app/var/oidc/private.pem"},
    {"name": "SIRTA_PUBLIC_OPEN_UI_BOOTSTRAP", "value": "true"},
]


def aws_json(args: list[str]) -> dict:
    out = subprocess.check_output(
        ["aws", *args, "--region", REGION, "--output", "json"], text=True
    )
    return json.loads(out)


def register(family: str, service: str, image: str, *, environment: list[dict] | None) -> str:
    td = aws_json(["ecs", "describe-task-definition", "--task-definition", family])[
        "taskDefinition"
    ]
    containers = td["containerDefinitions"]
    containers[0]["image"] = image
    if environment is not None:
        containers[0]["environment"] = environment
    payload = {
        "family": td["family"],
        "taskRoleArn": td.get("taskRoleArn"),
        "executionRoleArn": td.get("executionRoleArn"),
        "networkMode": td.get("networkMode"),
        "containerDefinitions": containers,
        "requiresCompatibilities": td.get("requiresCompatibilities"),
        "cpu": td.get("cpu"),
        "memory": td.get("memory"),
    }
    if td.get("volumes"):
        payload["volumes"] = td["volumes"]
    payload = {k: v for k, v in payload.items() if v is not None}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(payload, handle)
        path = handle.name
    try:
        registered = aws_json(
            ["ecs", "register-task-definition", "--cli-input-json", f"file://{path}"]
        )
        arn = registered["taskDefinition"]["taskDefinitionArn"]
        aws_json(
            [
                "ecs",
                "update-service",
                "--cluster",
                CLUSTER,
                "--service",
                service,
                "--task-definition",
                arn,
                "--force-new-deployment",
            ]
        )
        return arn
    finally:
        os.unlink(path)


def main() -> None:
    lines = [
        f"api={register('sirta-prod-api', 'sirta-prod-api', API_IMAGE, environment=API_ENV)}",
        f"web={register('sirta-prod-web', 'sirta-prod-web', WEB_IMAGE, environment=None)}",
    ]
    print("waiting for stable...")
    subprocess.check_call(
        [
            "aws",
            "ecs",
            "wait",
            "services-stable",
            "--cluster",
            CLUSTER,
            "--services",
            "sirta-prod-api",
            "sirta-prod-web",
            "--region",
            REGION,
        ]
    )
    lines.append("STABLE")
    Path("evidence/ops/ecs-redeploy-0.3.101.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print("\n".join(lines))


if __name__ == "__main__":
    main()
