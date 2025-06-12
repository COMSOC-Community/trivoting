from unittest import TestCase

from trivoting.election.alternative import Alternative


class TestAlternative(TestCase):
    def test_alternative(self):
        a = Alternative("a")
        b = Alternative("b")
        a2 = Alternative("a")

        self.assertNotEqual(a, b)
        self.assertEqual(a, a2)