import logging

log = logging.getLogger(__name__)

class VoicePipeline:
    def __init__(self, config):
        self.config = config.get("voice", {})

    async def transcribe(self, wav_path: str) -> str:
        try:
            from faster_whisper import WhisperModel
            stt = self.config.get("stt", {})
            model = WhisperModel(stt.get("model", "small"), device=stt.get("device", "auto"), compute_type=stt.get("compute_type", "int8"))
            segments, _ = model.transcribe(wav_path, language=stt.get("language", "vi"))
            return " ".join(s.text.strip() for s in segments)
        except Exception as exc:
            log.exception("STT unavailable")
            return ""

class WakeWord:
    def __init__(self, word="neura"):
        self.word = word.lower()
    def matches(self, text):
        return self.word in text.lower()
