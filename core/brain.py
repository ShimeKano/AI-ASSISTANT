import json
import re
from core.registry import ToolResult

SYSTEM = '''You are Neura, a Vietnamese Windows assistant. Return ONLY JSON:
{"actions":[{"tool":"tool.name","arguments":{}}],"reply":"..."}
Use only supplied tools. Never invent tools. Prefer no action when a request is conversational.
'''

class Brain:
    def __init__(self, config, registry, events, conversation, llm):
        self.registry, self.events, self.conversation, self.llm = registry, events, conversation, llm

    async def plan(self, text):
        self.conversation.add("user", text)
        if not self.llm.enabled:
            return self.fallback(text)
        prompt = SYSTEM + "\nTOOLS:\n" + json.dumps(self.registry.schemas(), ensure_ascii=False) + "\nHISTORY:\n" + self.conversation.text() + "\nUSER:\n" + text
        raw = await self.llm.complete(prompt)
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return [], raw.strip() or "Mình chưa hiểu yêu cầu."
        try:
            obj = json.loads(match.group(0))
            actions = [a for a in obj.get("actions", []) if self.registry.has(a.get("tool", ""))]
            return actions, obj.get("reply", "Đã xử lý.")
        except (json.JSONDecodeError, TypeError):
            return [], "Mình chưa hiểu yêu cầu đó."

    def fallback(self, text):
        t = text.lower()
        if "youtube" in t:
            return [{"tool": "youtube.search", "arguments": {"query": ""}}], "Mình mở YouTube cho bạn."
        if "word" in t and "mở" in t:
            return [{"tool": "word.open", "arguments": {}}], "Mình mở Word cho bạn."
        return [], "Mình đang ở chế độ offline. Hãy cấu hình OpenRouter hoặc Ollama để dùng hội thoại tự nhiên."

    async def handle(self, text, context):
        await self.events.emit("brain.thinking", text=text)
        actions, reply = await self.plan(text)
        results = []
        for action in actions:
            await self.events.emit("action.started", tool=action["tool"])
            result = await context.safety.execute(action, self.registry, context)
            results.append(result)
            await self.events.emit("action.finished", tool=action["tool"], result=result)
        self.conversation.add("assistant", reply)
        await self.events.emit("assistant.reply", text=reply)
        return reply, results
