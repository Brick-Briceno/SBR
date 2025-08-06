class SBR_ERROR(Exception):
    def __init__(self, message="", advice=None):
        self.message, self.advice = message, advice
        super().__init__()

    def __str__(self):
        return (self.message if self.advice is None
         else f"{self.message} ({self.advice})")
