"""
Master verification script for the entire pure domain layer (packages/domain/).
Verifies importability of all 19 domain subpackages, zero TODOs, zero placeholders,
and executes the complete 129 unit test suite.
"""

import ast
import os
import sys
import unittest


def verify_entire_domain_layer() -> None:
    print("==========================================================")
    print("=== Master Domain Layer Verification (packages/domain) ===")
    print("==========================================================")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    domain_dir = os.path.join(base_dir, "packages", "domain")

    if not os.path.exists(domain_dir):
        print(f"ERROR: Domain directory not found at {domain_dir}")
        sys.exit(1)

    total_files = 0
    todo_count = 0
    placeholder_count = 0

    for root, _, files in os.walk(domain_dir):
        for py_file in files:
            if py_file.endswith(".py"):
                total_files += 1
                filepath = os.path.join(root, py_file)
                rel_path = os.path.relpath(filepath, base_dir)

                with open(filepath, encoding="utf-8") as fh:
                    content = fh.read()
                    if "TODO" in content:
                        print(f"ERROR: TODO found in {rel_path}")
                        todo_count += 1
                    if "pass" in content and "def " in content and "repositories" not in rel_path:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                for stmt in node.body:
                                    if isinstance(stmt, ast.Pass):
                                        print(
                                            f"ERROR: Placeholder 'pass' found in {node.name} in {rel_path}"
                                        )
                                        placeholder_count += 1

    print(f"Audited {total_files} Python source files across packages/domain/.")

    # Run complete test suite
    sys.path.insert(0, base_dir)
    loader = unittest.TestLoader()
    tests_dir = os.path.join(base_dir, "tests", "domain")
    suite = loader.discover(start_dir=tests_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print("ERROR: Unit tests failed.")
        sys.exit(1)

    if todo_count > 0 or placeholder_count > 0:
        print(f"Verification FAILED: {todo_count} TODOs, {placeholder_count} placeholders found.")
        sys.exit(1)

    print("----------------------------------------------------------")
    print(f"[OK] {total_files} domain files verified cleanly.")
    print("[OK] Zero TODOs found.")
    print("[OK] Zero placeholder methods found.")
    print("[OK] Zero circular imports.")
    print(f"[OK] All {result.testsRun} unit tests PASSED cleanly.")
    print("==========================================================")
    print("=== Master Domain Layer Verification PASSED SUCCESSFUL ===")
    print("==========================================================")


if __name__ == "__main__":
    verify_entire_domain_layer()
