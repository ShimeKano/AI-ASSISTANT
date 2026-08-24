from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ToolResult:
    ok: bool
    message: str
    data: Any = None

class Tool(ABC):
    name = ""
    description = ""
    risk = "low"

    def schema(self):
        return {"name": self.name, "description": self.description, "risk": self.risk}

    @abstractmethod
    async def execute(self, arguments: dict, context) -> ToolResult:
        raise NotImplementedError

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        if not tool.name:
            raise ValueError("Tool name is required")
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def schemas(self):
        return [t.schema() for t in self._tools.values()]
