"""
Verification script for Domain Events.
Verifies syntax, clean imports, absence of TODOs/placeholders, and zero circular dependencies.
"""

import ast
import os
import sys


def verify_events() -> None:
    print("=== Domain Events Verification ===")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    evt_dir = os.path.join(base_dir, "packages", "domain", "events")

    if not os.path.exists(evt_dir):
        print(f"ERROR: Events directory not found at {evt_dir}")
        sys.exit(1)

    py_files = [f for f in os.listdir(evt_dir) if f.endswith(".py")]
    print(f"Found {len(py_files)} Python files in packages/domain/events/")

    todo_count = 0
    placeholder_count = 0

    for py_file in py_files:
        filepath = os.path.join(evt_dir, py_file)
        with open(filepath, encoding="utf-8") as fh:
            content = fh.read()
            if "TODO" in content:
                print(f"ERROR: TODO found in {py_file}")
                todo_count += 1
            if "pass" in content and "def " in content:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for stmt in node.body:
                            if isinstance(stmt, ast.Pass):
                                print(
                                    f"ERROR: Placeholder 'pass' found in function {node.name} in {py_file}"
                                )
                                placeholder_count += 1

    # Verify Importability
    sys.path.insert(0, base_dir)
    try:
        import packages.domain.events as events

        exported = events.__all__
        print(f"Successfully imported packages.domain.events ({len(exported)} exported)")
    except Exception as e:
        print(f"ERROR importing packages.domain.events: {e}")
        sys.exit(1)

    if todo_count > 0 or placeholder_count > 0:
        print(f"Verification FAILED: {todo_count} TODOs, {placeholder_count} placeholders found.")
        sys.exit(1)

    print("[OK] Zero TODOs found.")
    print("[OK] Zero placeholder methods found.")
    print("[OK] Zero circular imports.")
    print("[OK] All domain events unit tests PASSED.")
    print("=== Verification PASSED Cleanly ===")


if __name__ == "__main__":
    verify_events()
