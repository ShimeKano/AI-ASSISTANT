from core.registry import ToolResult

class SafetyController:
    def __init__(self, config, events):
        self.blocked = set(config.get("blocked_tools", []))
        self.confirm = set(config.get("require_confirmation", []))
        self.stopped = False
        self.events = events

    def emergency_stop(self):
        self.stopped = True

    def release(self):
        self.stopped = False

    async def execute(self, action, registry, context):
        if self.stopped:
            return ToolResult(False, "Emergency stop is active.")
        if action["tool"] in self.blocked:
            return ToolResult(False, f"Blocked tool: {action['tool']}")
        if action["tool"] in self.confirm:
            return ToolResult(False, f"Confirmation required: {action['tool']}")
        try:
            return await registry.get(action["tool"]).execute(action.get("arguments", {}), context)
        except Exception as exc:
            await self.events.emit("tool.error", tool=action["tool"], error=str(exc))
            return ToolResult(False, str(exc))
