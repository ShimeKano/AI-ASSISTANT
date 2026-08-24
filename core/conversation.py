from collections import deque

class Conversation:
    def __init__(self, limit=30):
        self.messages = deque(maxlen=limit)

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def text(self):
        return "\n".join(f"{m['role']}: {m['content']}" for m in self.messages)
