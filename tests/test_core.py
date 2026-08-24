import asyncio
from core.registry import Tool, ToolRegistry, ToolResult
from core.events import EventBus
from safety.controller import SafetyController

class Dummy(Tool):
    name = "test.dummy"
    description = "test tool"
    async def execute(self, arguments, context):
        return ToolResult(True, "ok")

def test_registry():
    r = ToolRegistry(); r.register(Dummy())
    assert r.has("test.dummy")

def test_emergency_stop():
    bus = EventBus(); safety = SafetyController({}, bus); r = ToolRegistry(); r.register(Dummy())
    safety.emergency_stop()
    result = asyncio.run(safety.execute({"tool":"test.dummy","arguments":{}}, r, None))
    assert result.ok is False
