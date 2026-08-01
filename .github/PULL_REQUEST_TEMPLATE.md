## Summary
<!-- Concise 2-3 sentence overview of the changes introduced in this Pull Request. -->

## Related Issue
<!-- Link to the issue this PR resolves or addresses (e.g. Closes #123, Fixes #456). -->

## Architecture Impact
<!-- Detail any structural impact on Clean Architecture layers or service interfaces. State "None" if purely internal logic. -->

## DDD Impact
<!-- Detail any modifications to Bounded Contexts, Aggregate Roots, Entities, Value Objects, Domain Events, or Policies. -->

## Implementation Details
<!-- Summary of technical changes, new classes/methods, or algorithms added. -->

## Testing
<!-- Detail automated and manual testing performed. Paste output command results. -->
```bash
# Example test execution command and result
python -m unittest discover -s tests/domain -p "test_*.py"
```

## Checklist
- [ ] Code compiles and passes all unit tests cleanly.
- [ ] Static type checking (`mypy --strict`) passes with zero errors.
- [ ] Linting (`ruff check .`, `black --check .`) passes with zero warnings.
- [ ] No TODOs, FIXME comments, or placeholder methods remain in production code.
- [ ] Follows financial software rules (Decimal for money, timezone-aware datetimes).

## Documentation Updated
- [ ] Public API docstrings (PEP 257) added/updated.
- [ ] Relevant documentation in `docs/` updated.
- [ ] ADR created in `docs/adr/` (if architectural decision was made).

## Performance Impact
<!-- Describe any impact on runtime latency, memory usage, or computational complexity. -->

## Security Impact
<!-- Confirm zero hardcoded credentials, input validation, and adherence to security principles. -->

## Breaking Changes
<!-- List any breaking API or domain contract changes. Detail migration instructions if applicable. -->

## Reviewer Notes
<!-- Special instructions or focus areas for code reviewers. -->
