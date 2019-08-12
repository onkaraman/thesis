class SpamChecker:
    def __init__(self):
        self.stop_words = ["sex", "sexy", "hot", "casino", "gesundheit", "dating", "girls",
                           "http:"]

    def contains_stop_words(self, content):
        for c in self.stop_words:
            if c in content:
                return True
        return False


