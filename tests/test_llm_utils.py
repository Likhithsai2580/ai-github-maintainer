import unittest
from unittest.mock import patch
from llm_utils import generate_command

class TestGenerateCommandCaching(unittest.TestCase):

    @patch('llm_utils.completion')
    def test_generate_command_caching(self, mock_completion):
        # Mock the completion function to return a fixed response
        mock_completion.return_value.choices[0].message.content = "Mocked response"

        # First call to generate_command
        response1 = generate_command("Test prompt")
        self.assertEqual(response1, "Mocked response")

        # Second call to generate_command with the same prompt
        response2 = generate_command("Test prompt")
        self.assertEqual(response2, "Mocked response")

        # Ensure the completion function was called only once due to caching
        mock_completion.assert_called_once()

    @patch('llm_utils.completion')
    def test_generate_command_different_prompts(self, mock_completion):
        # Mock the completion function to return different responses
        mock_completion.side_effect = [
            lambda *args, **kwargs: type('obj', (object,), {'choices': [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Response 1'})})]})(),
            lambda *args, **kwargs: type('obj', (object,), {'choices': [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Response 2'})})]})()
        ]

        # Call generate_command with different prompts
        response1 = generate_command("Prompt 1")
        self.assertEqual(response1, "Response 1")

        response2 = generate_command("Prompt 2")
        self.assertEqual(response2, "Response 2")

        # Ensure the completion function was called twice
        self.assertEqual(mock_completion.call_count, 2)

if __name__ == '__main__':
    unittest.main()
