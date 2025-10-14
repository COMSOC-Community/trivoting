import string
from unittest import TestCase

from trivoting.fractions import frac
from trivoting.utils import generate_two_list_partitions, harmonic_sum


class TestUtils(TestCase):
    def test_split_in_two_lists(self):
        for l in range(0, 6):
            iterable = string.ascii_lowercase[:l]
            for k in range(0, len(iterable) + 1):
                num_element = 0
                all_elements = set()
                for c in generate_two_list_partitions(iterable, first_list_max_size=k):
                    num_element += 1
                    all_elements.add((tuple(c[0]), tuple(c[1])))
                    self.assertLessEqual(len(c[0]), k)
                self.assertEqual(len(all_elements), num_element)

            if l > 0:
                full_size = list(generate_two_list_partitions(iterable))
                self.assertEqual(len(full_size), 3**l)

    def test_harmonic(self):
        self.assertEqual(harmonic_sum(0), 0)
        self.assertEqual(harmonic_sum(1), 1)
        self.assertEqual(harmonic_sum(2), frac(3, 2))
        self.assertEqual(harmonic_sum(3), frac(11, 6))
        self.assertEqual(harmonic_sum(-1), 0)
        self.assertEqual(harmonic_sum(-2), 0)
