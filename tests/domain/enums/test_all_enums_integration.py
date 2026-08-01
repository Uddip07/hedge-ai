"""
Comprehensive Integration Unit Tests for All Domain Enums.
Checks member uniqueness, string serialization, documentation, and module exports.
"""

import unittest

import packages.domain.enums as domain_enums


class TestAllDomainEnumsIntegration(unittest.TestCase):
    """Test suite covering all domain enum exports."""

    def test_all_exported_enums(self):
        exported_names = domain_enums.__all__
        self.assertGreater(len(exported_names), 20)

        for name in exported_names:
            enum_cls = getattr(domain_enums, name)
            self.assertIsNotNone(enum_cls.__doc__, f"Enum {name} must have a docstring")
            # Verify uniqueness of values
            values = [item.value for item in enum_cls]
            self.assertEqual(
                len(values),
                len(set(values)),
                f"Enum {name} contains duplicate values: {values}",
            )
            # Verify StrEnum string conversion
            for item in enum_cls:
                self.assertEqual(str(item), item.value)


if __name__ == "__main__":
    unittest.main()
