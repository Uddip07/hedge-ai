"""
Tool Registry for AI Core Framework.

Central manager for registering and executing tools invoked by agents.
"""

from typing import Any

from packages.ai.tools.base_tool import BaseTool


class ToolRegistry:
    """
    Registry for managing available agent tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        """Register a BaseTool instance."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Retrieve tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry.")
        return self._tools[name]

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a registered tool by name with provided arguments."""
        tool = self.get_tool(name)
        return tool.execute(arguments)

    def list_tools(self) -> list[dict[str, str]]:
        """List metadata for all registered tools."""
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]
