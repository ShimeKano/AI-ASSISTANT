import asyncio
from dataclasses import dataclass
from pathlib import Path
import yaml
from core.registry import ToolRegistry
from core.events import EventBus
from core.conversation import Conversation
from core.brain import Brain
from providers.llm import LLMClient
from safety.controller import SafetyController
from tools.system import OpenApp, MouseClick, TypeText, PressKey, MediaKey
from tools.browser import OpenURL, YouTube
from tools.office import WordOpen, WordType
from tools.vision import Screenshot, OCRScreen, ClickText
from gui.overlay import Overlay

@dataclass
class Context:
    config: dict
    events: EventBus
    safety: SafetyController
    conversation: Conversation

class Application:
    def __init__(self):
        with Path("config.yaml").open(encoding="utf-8") as f: config = yaml.safe_load(f) or {}
        self.events = EventBus()
        self.registry = ToolRegistry()
        self.safety = SafetyController(config.get("safety", {}), self.events)
        self.conversation = Conversation()
        self.context = Context(config, self.events, self.safety, self.conversation)
        for tool in [OpenApp(), MouseClick(), TypeText(), PressKey(), MediaKey(), OpenURL(), YouTube(), WordOpen(), WordType(), Screenshot(), OCRScreen(), ClickText()]:
            self.registry.register(tool)
        self.brain = Brain(config, self.registry, self.events, self.conversation, LLMClient(config.get("llm", {})))
        self.overlay = Overlay(self.brain, self.context)

    def run(self):
        self.overlay.run()
