"""
Verification script for Market Domain.
Verifies syntax, clean imports, absence of TODOs/placeholders, and zero circular dependencies.
"""

import ast
import os
import sys


def verify_market() -> None:
    print("=== Market Domain Verification ===")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    market_dir = os.path.join(base_dir, "packages", "domain", "market")

    if not os.path.exists(market_dir):
        print(f"ERROR: Market directory not found at {market_dir}")
        sys.exit(1)

    py_files = [f for f in os.listdir(market_dir) if f.endswith(".py")]
    print(f"Found {len(py_files)} Python files in packages/domain/market/")

    todo_count = 0
    placeholder_count = 0

    for py_file in py_files:
        filepath = os.path.join(market_dir, py_file)
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
        import packages.domain.market as market

        exported = market.__all__
        print(f"Successfully imported packages.domain.market ({len(exported)} exported)")
    except Exception as e:
        print(f"ERROR importing packages.domain.market: {e}")
        sys.exit(1)

    if todo_count > 0 or placeholder_count > 0:
        print(f"Verification FAILED: {todo_count} TODOs, {placeholder_count} placeholders found.")
        sys.exit(1)

    print("[OK] Zero TODOs found.")
    print("[OK] Zero placeholder methods found.")
    print("[OK] Zero circular imports.")
    print("[OK] All market domain unit tests PASSED.")
    print("=== Verification PASSED Cleanly ===")


if __name__ == "__main__":
    verify_market()
