
import unittest
from dynamic_function import calculate_average


class TestCalculateAverage(unittest.TestCase):
    def test_normal_cases(self):
        self.assertEqual(calculate_average([1, 2, 3]), 2.0)

if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
