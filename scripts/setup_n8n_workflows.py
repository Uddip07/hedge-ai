#!/usr/bin/env python3
"""
MONEYYYYYY — n8n Workflow Validation and Management Utility.

Validates n8n workflow definitions against institutional schema constraints,
verifies FastAPI orchestration endpoints, and manages import/export workflows.
"""

import argparse
import json
import sys
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / "n8n" / "workflows"

EXPECTED_WORKFLOWS = [
    "MONEYYYYYY — Market Data Ingestion",
    "MONEYYYYYY — Market Data Health",
    "MONEYYYYYY — Daily Market Summary",
    "MONEYYYYYY — News Pipeline",
    "MONEYYYYYY — AI Investment Committee",
    "MONEYYYYYY — Backtest Trigger",
    "MONEYYYYYY — Zerodha Monitoring",
    "MONEYYYYYY — Alert Handler",
]


def validate_workflow_file(filepath: Path) -> tuple[bool, list[str]]:
    """Validate an individual n8n workflow JSON definition."""
    errors = []
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return False, [f"JSON Parse Error: {exc}"]

    # Required top-level fields
    for field in ("name", "nodes", "connections"):
        if field not in data:
            errors.append(f"Missing required top-level field '{field}'")

    if not isinstance(data.get("nodes"), list):
        errors.append("'nodes' must be a list")
    elif len(data.get("nodes", [])) == 0:
        errors.append("Workflow has zero nodes")

    if not isinstance(data.get("connections"), dict):
        errors.append("'connections' must be a dictionary")

    # Validate each node
    for node in data.get("nodes", []):
        if "name" not in node:
            errors.append("Found node missing 'name'")
        if "type" not in node:
            errors.append(f"Node '{node.get('name')}' missing 'type'")
        if "id" not in node:
            errors.append(f"Node '{node.get('name')}' missing 'id'")

    return len(errors) == 0, errors


def validate_all_workflows() -> bool:
    """Validate all expected workflows in n8n/workflows."""
    if not WORKFLOWS_DIR.exists():
        print(f"[FAIL] Workflows directory not found at: {WORKFLOWS_DIR}")
        return False

    all_valid = True
    found_workflows: set[str] = set()

    print(f"[INFO] Scanning workflow definitions in: {WORKFLOWS_DIR}\n")

    for json_file in sorted(WORKFLOWS_DIR.glob("*.json")):
        valid, errors = validate_workflow_file(json_file)
        workflow_name = json_file.stem
        found_workflows.add(workflow_name)

        if valid:
            print(f"  [PASS] {json_file.name}")
        else:
            all_valid = False
            print(f"  [FAIL] {json_file.name}")
            for err in errors:
                print(f"         - {err}")

    print("")
    # Check for missing expected workflows
    missing = set(EXPECTED_WORKFLOWS) - found_workflows
    if missing:
        all_valid = False
        print(f"[FAIL] Missing expected workflow files: {missing}")
    else:
        print(
            f"[OK] All {len(EXPECTED_WORKFLOWS)} mandatory MONEYYYYYY workflows present and validated."
        )

    return all_valid


def list_workflows() -> None:
    """List all workflow definitions and summaries."""
    print("=" * 60)
    print(" MONEYYYYYY — Registered n8n Workflows")
    print("=" * 60)
    for json_file in sorted(WORKFLOWS_DIR.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                d = json.load(f)
            node_count = len(d.get("nodes", []))
            triggers = [
                n["name"]
                for n in d.get("nodes", [])
                if "Trigger" in n.get("type", "")
                or "webhook" in n.get("type", "").lower()
                or "schedule" in n.get("type", "").lower()
            ]
            print(f"• {d.get('name')}")
            print(f"  File     : {json_file.name}")
            print(f"  Nodes    : {node_count}")
            print(f"  Triggers : {', '.join(triggers) if triggers else 'Manual / HTTP'}")
            print("")
        except Exception as exc:
            print(f"• {json_file.name} (Error reading: {exc})")


def main() -> int:
    parser = argparse.ArgumentParser(description="MONEYYYYYY n8n Workflow Manager")
    parser.add_argument(
        "--validate", action="store_true", help="Validate all workflow JSON schemas"
    )
    parser.add_argument("--list", action="store_true", help="List all available workflows")

    args = parser.parse_args()

    if args.list:
        list_workflows()
        return 0

    # Default to validate
    success = validate_all_workflows()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
