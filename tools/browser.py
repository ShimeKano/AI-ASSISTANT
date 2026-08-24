import webbrowser
from urllib.parse import quote_plus
from core.registry import Tool, ToolResult

class OpenURL(Tool):
    name = "browser.open_url"
    description = "Open a URL in the default Windows browser."
    async def execute(self, arguments, context):
        url = str(arguments.get("url", "")).strip()
        if not url.startswith(("http://", "https://")): url = "https://" + url
        webbrowser.open(url)
        return ToolResult(True, f"Opened {url}")

class YouTube(Tool):
    name = "youtube.search"
    description = "Open YouTube and optionally search for a video, music or film."
    async def execute(self, arguments, context):
        q = str(arguments.get("query", "")).strip()
        url = "https://www.youtube.com" + ("/results?search_query=" + quote_plus(q) if q else "")
        webbrowser.open(url)
        return ToolResult(True, "YouTube opened")
