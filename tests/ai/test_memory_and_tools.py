"""
Unit tests for ConversationStore and ToolRegistry.
"""

import unittest
from typing import Any

from packages.ai.memory import ConversationStore
from packages.ai.tools import BaseTool, ToolRegistry


class DummyTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_calculator"

    @property
    def description(self) -> str:
        return "Performs dummy math calculations."

    def execute(self, arguments: dict[str, Any]) -> Any:
        return arguments.get("a", 0) + arguments.get("b", 0)


class TestMemoryAndTools(unittest.TestCase):
    def test_conversation_store_crud(self) -> None:
        store = ConversationStore()
        session_id = "test-session-123"

        store.add_message(session_id, "user", "Analyze RELIANCE")
        history = store.get_history(session_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "Analyze RELIANCE")

        store.clear_session(session_id)
        self.assertEqual(len(store.get_history(session_id)), 0)

    def test_tool_registry_registration_and_execution(self) -> None:
        registry = ToolRegistry()
        tool = DummyTool()

        registry.register_tool(tool)
        self.assertEqual(len(registry.list_tools()), 1)

        result = registry.execute_tool("dummy_calculator", {"a": 10, "b": 20})
        self.assertEqual(result, 30)

        with self.assertRaises(KeyError):
            registry.get_tool("non_existent_tool")


if __name__ == "__main__":
    unittest.main()
