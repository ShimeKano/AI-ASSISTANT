from pathlib import Path
from datetime import datetime
import os
import pyautogui
from core.registry import Tool, ToolResult

class Screenshot(Tool):
    name = "screen.capture"
    description = "Capture the Windows screen to data/screenshots."
    async def execute(self, arguments, context):
        folder = Path("data/screenshots")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"screen_{datetime.now():%Y%m%d_%H%M%S}.png"
        pyautogui.screenshot(str(path))
        return ToolResult(True, str(path), str(path))

class OCRScreen(Tool):
    name = "screen.read_text"
    description = "Read visible screen text using Tesseract OCR."
    async def execute(self, arguments, context):
        import pytesseract
        cmd = os.getenv("TESSERACT_CMD")
        if cmd: pytesseract.pytesseract.tesseract_cmd = cmd
        text = pytesseract.image_to_string(pyautogui.screenshot(), lang="eng")
        return ToolResult(True, text.strip() or "No text detected", text.strip())

class ClickText(Tool):
    name = "screen.click_text"
    description = "Find a visible label with OCR and click its center."
    async def execute(self, arguments, context):
        import pytesseract
        from pytesseract import Output
        target = str(arguments.get("text", "")).lower().strip()
        if not target: return ToolResult(False, "No text supplied")
        data = pytesseract.image_to_data(pyautogui.screenshot(), output_type=Output.DICT, lang="eng")
        for i, word in enumerate(data["text"]):
            if target in word.lower():
                x = int(data["left"][i] + data["width"][i] / 2)
                y = int(data["top"][i] + data["height"][i] / 2)
                pyautogui.click(x, y)
                return ToolResult(True, f"Clicked {word} at {x},{y}")
        return ToolResult(False, f"Could not find {target}")
