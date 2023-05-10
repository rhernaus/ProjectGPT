import unittest
import app
import os
from unittest.mock import patch

class TestApp(unittest.TestCase):

    def test_get_api_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            api_key = app.get_api_key()
        self.assertEqual(api_key, "test_key")

    def test_get_api_key_none(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            api_key = app.get_api_key()
        self.assertEqual(api_key, "")

if __name__ == '__main__':
    unittest.main()