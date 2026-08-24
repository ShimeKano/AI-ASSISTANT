# Neura Assistant

A modular Windows 11 desktop assistant for hands-free computer support. The target user can still speak but may have limited or no ability to use a mouse/keyboard.

## Design goals

- Voice-first interaction with optional text UI fallback.
- Anime/Live2D avatar isolated behind an interface.
- LLM can plan actions, but never receives direct OS access.
- Every computer action is a registered Tool and passes through SafetyController.
- New features are added as tools/plugins instead of modifying the brain.
- Emergency stop is available from the desktop UI and `Ctrl+Shift+F12`.

## Architecture

```text
Microphone -> STT -> Brain/Planner -> SafetyController -> ToolRegistry
                                      |                  |-> Windows
                                      |                  |-> Browser/YouTube
                                      |                  |-> Word
                                      |                  |-> Vision/OCR
                                      v
                                   Events -> GUI/Avatar
                                      |
                                      v
                                     TTS
```

## Current implementation

- OpenRouter and Ollama LLM providers.
- Tool registry with schemas and risk metadata.
- Conversation memory and event bus.
- Windows app launcher, mouse click, typing, keyboard shortcuts and media keys.
- Browser/YouTube tools.
- Microsoft Word COM tools.
- Screenshot, OCR and click-by-visible-text tools.
- Optional Faster-Whisper STT and Edge-TTS provider.
- Tkinter desktop control panel.
- Safety blocklist, confirmation boundary and emergency stop.
- Avatar abstraction ready for a Live2D renderer.
- Basic tests.

## Install on Windows 11

Use Python 3.11+:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

Set an OpenRouter key:

```powershell
$env:OPENROUTER_API_KEY="YOUR_KEY"
python main.py
```

Or use Ollama by changing `config.yaml` to `provider: ollama` and setting its local URL/model.

## Vision prerequisites

`pytesseract` is only the Python bridge. Install Tesseract OCR on Windows and optionally set:

```powershell
$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Voice

Faster-Whisper and sounddevice are included as optional dependencies. A first Whisper model load/download can take time. The application still works through the text UI if voice dependencies are unavailable.

## Adding a feature safely

Create a class implementing `core.registry.Tool`, give it a unique `name`, implement `execute()`, register it in `core/application.py`, and add a test. Do not add feature-specific logic to `Brain` or `SafetyController` unless it is a global policy.

Example:

```python
class SpotifyOpen(Tool):
    name = "spotify.open"
    description = "Open Spotify."

    async def execute(self, arguments, context):
        ...
```

This makes features replaceable and prevents the assistant from becoming one giant conditional command handler.

## Safety notes

The assistant is intentionally designed so the LLM proposes named actions rather than executing arbitrary Python or shell commands. High-impact operations can be put in `require_confirmation`, and emergency stop blocks all tool execution.
