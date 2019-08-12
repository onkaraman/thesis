import uuid
from django.test import TestCase
from datetime import timedelta
from security_token.models import SecurityToken


class TestsSecurityTokenModel(TestCase):
    def test_creation_valid(self):
        st = SecurityToken()
        st.code = str(uuid.uuid4())
        try:
            st.save()
            self.assertTrue(True)
        except Exception:
            self.assertFalse("Couldn't save valid object")

    def test_code_too_short(self):
        st = SecurityToken()
        st.code = "a1b2c3"
        try:
            st.save()
            self.assertFalse("Could save token with too short code")
        except Exception:
            self.assertTrue(True)

    def test_code_only_numbers(self):
        st = SecurityToken()
        st.code = "abc"*10
        try:
            st.save()
            self.assertFalse("Could save token with only letters code")
        except Exception:
            self.assertTrue(True)

    def test_too_short_expiration(self):
        st = SecurityToken()
        st.code = "abc1" * 10
        st.expiration_after_days = 0
        try:
            st.save()
            self.assertFalse("Could save token with too short expiration")
        except Exception:
            self.assertTrue(True)

    def test_does_expire(self):
        st = SecurityToken()
        st.code = "abc1" * 10
        d = timedelta(days=30)
        st.save()
        st.creation_date -= d
        st.save()

        if st.has_expired():
            self.assertTrue(True)
        else:
            self.assertFalse("Token not expiring")