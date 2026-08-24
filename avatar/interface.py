class Avatar:
    """Stable interface for Live2D/anime rendering without coupling it to the brain."""
    def show(self): pass
    def hide(self): pass
    def set_emotion(self, emotion: str): pass
    def set_speaking(self, speaking: bool): pass
