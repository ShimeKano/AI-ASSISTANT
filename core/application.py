import asyncio
import os
import re
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


_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(:-([^}]*))?\}")


def _expand_env(value: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(3)
        return os.getenv(name, default or "")

    return _ENV_PATTERN.sub(replace, value)


@dataclass
class Context:
    config: dict
    events: EventBus
    safety: SafetyController
    conversation: Conversation


class Application:
    def __init__(self):
        config_path = Path("config.yaml")
        raw_config = config_path.read_text(encoding="utf-8")
        config = yaml.safe_load(_expand_env(raw_config)) or {}

        self.events = EventBus()
        self.registry = ToolRegistry()
        self.safety = SafetyController(config.get("safety", {}), self.events)
        self.conversation = Conversation()
        self.context = Context(config, self.events, self.safety, self.conversation)

        for tool in [
            OpenApp(), MouseClick(), TypeText(), PressKey(), MediaKey(),
            OpenURL(), YouTube(), WordOpen(), WordType(), Screenshot(),
            OCRScreen(), ClickText(),
        ]:
            self.registry.register(tool)

        self.brain = Brain(
            config,
            self.registry,
            self.events,
            self.conversation,
            LLMClient(config.get("llm", {})),
        )
        self.overlay = Overlay(self.brain, self.context)

    def run(self):
        self.overlay.run()
