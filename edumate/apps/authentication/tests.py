from django.core import mail
from django.test import SimpleTestCase, override_settings

from apps.authentication.security import send_code


class SendCodeTests(SimpleTestCase):
    @override_settings(
        MAILERS={
            "default": {
                "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
            }
        }
    )
    def test_sends_verification_code_to_recipient(self):
        sent_count = send_code("student@example.com", "123456")

        self.assertEqual(sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])
        self.assertIn("123456", mail.outbox[0].body)
