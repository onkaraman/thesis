import random
import string


class PasswordGenerator:

    @staticmethod
    def generate(len_chars=5, len_numbers=3, len_special=2):
        ab = list(string.ascii_uppercase)
        no = list(range(0, 10))
        special = ["-", "+", "?", "!", "."]

        pw = ""
        for i in range(len_chars):
            pw += ab[random.randint(0, len(ab)-1)]
        for i in range(len_numbers):
            pw += str(no[random.randint(0, len(no)-1)])
        for i in range(len_special):
            pw += special[random.randint(0, len(special)-1)]

        return pw
