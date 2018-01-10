class DenonTrigger(object):
    """docstring for DenonInput"""
    def __init__(self, keywords, voice_modes):
        super(DenonInput, self).__init__()
        self.keywords = keywords
        self.voice_modes = voice_modes

    def triggers(self):
        return self.keywords