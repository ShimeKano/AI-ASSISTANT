from pathlib import Path
import tempfile

class EdgeTTS:
    def __init__(self, config):
        self.config = config.get("voice", {}).get("tts", {})

    async def synthesize(self, text):
        import edge_tts
        path = Path(tempfile.gettempdir()) / "neura_reply.mp3"
        await edge_tts.Communicate(text, self.config.get("voice", "vi-VN-HoaiMyNeural"), rate=self.config.get("rate", "+0%"), volume=self.config.get("volume", "+0%")).save(str(path))
        return str(path)
