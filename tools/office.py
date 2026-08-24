from core.registry import Tool, ToolResult

class WordOpen(Tool):
    name = "word.open"
    description = "Open Microsoft Word and create a blank document."
    async def execute(self, arguments, context):
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        word.Documents.Add()
        return ToolResult(True, "Word opened")

class WordType(Tool):
    name = "word.type"
    description = "Insert text into the active Word document."
    async def execute(self, arguments, context):
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        if word.Documents.Count == 0: word.Documents.Add()
        word.Selection.TypeText(str(arguments.get("text", "")))
        return ToolResult(True, "Text inserted into Word")
