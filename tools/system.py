import subprocess
import webbrowser
import pyautogui
from core.registry import Tool, ToolResult

APPS = {"notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe", "word": "winword.exe", "explorer": "explorer.exe"}

class OpenApp(Tool):
    name = "system.open_app"
    description = "Open a Windows application by name or executable."
    async def execute(self, arguments, context):
        app = str(arguments.get("app", "")).strip().lower()
        if not app: return ToolResult(False, "No app supplied")
        subprocess.Popen(APPS.get(app, app), shell=True)
        return ToolResult(True, f"Opened {app}")

class MouseClick(Tool):
    name = "system.mouse_click"
    description = "Click a screen coordinate."
    async def execute(self, arguments, context):
        x, y = int(arguments["x"]), int(arguments["y"])
        pyautogui.click(x, y)
        return ToolResult(True, f"Clicked {x},{y}")

class TypeText(Tool):
    name = "system.type_text"
    description = "Type text into the focused application."
    async def execute(self, arguments, context):
        pyautogui.write(str(arguments.get("text", "")), interval=0.01)
        return ToolResult(True, "Text typed")

class PressKey(Tool):
    name = "system.press_key"
    description = "Press a key or shortcut such as ctrl+s."
    async def execute(self, arguments, context):
        key = str(arguments.get("key", "")).lower().replace(" ", "")
        if "+" in key: pyautogui.hotkey(*key.split("+"))
        else: pyautogui.press(key)
        return ToolResult(True, f"Pressed {key}")

class MediaKey(Tool):
    name = "system.media_key"
    description = "Control Windows media playback."
    async def execute(self, arguments, context):
        keys = {"playpause":"playpause", "next":"nexttrack", "previous":"prevtrack", "volumeup":"volumeup", "volumedown":"volumedown", "mute":"volumemute"}
        key = str(arguments.get("key", "playpause")).lower()
        if key not in keys: return ToolResult(False, "Unsupported media key")
        pyautogui.press(keys[key])
        return ToolResult(True, f"Media: {key}")
