
from app import generate_short_id

import unittest

"""
Code Analysis

Objective:
The objective of the function is to generate a short ID of a specified number of characters. This short ID can be used to create short URLs for a website.

Inputs:
- num_of_chars: an integer representing the number of characters the short ID should have.

Flow:
- The function uses the 'choice' method from the 'random' module to randomly select characters from the 'ascii_letters' and 'digits' strings.
- The 'join' method is used to concatenate the selected characters into a single string.
- The resulting string is returned as the short ID.

Outputs:
- A string representing the short ID of the specified number of characters.

Additional aspects:
- The function is used in the 'index' function to generate a short ID for a new short URL.
- The 'ascii_letters' and 'digits' strings are used to ensure that the generated short ID contains both letters and numbers.
"""
class TestGenerateShortId(unittest.TestCase):
    # Tests that the function generates a short_id of length 1
    def test_happy_path_num_of_chars_1(self):
        result = generate_short_id(1)
        self.assertEqual(len(result), 1)

    # Tests that the function generates a short_id of length 5
    def test_happy_path_num_of_chars_5(self):
        result = generate_short_id(5)
        self.assertEqual(len(result), 5)

    # Tests that the function generates a short_id of length 10
    def test_happy_path_num_of_chars_10(self):
        result = generate_short_id(10)
        self.assertEqual(len(result), 10)

    # Tests that the function generates a short_id of length 100
    def test_general_behaviour_num_of_chars_large(self):
        result = generate_short_id(100)
        self.assertEqual(len(result), 100)