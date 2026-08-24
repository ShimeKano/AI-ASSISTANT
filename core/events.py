from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import inspect

@dataclass
class Event:
    name: str
    data: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, name, handler):
        self._handlers[name].append(handler)

    async def emit(self, name, **data):
        event = Event(name, data)
        for handler in tuple(self._handlers.get(name, ())):
            result = handler(event)
            if inspect.isawaitable(result):
                await result
