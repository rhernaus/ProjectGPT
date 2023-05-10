import unittest
import projectgpt
from unittest.mock import MagicMock, patch

class TestProjectGPT(unittest.TestCase):

    def setUp(self):
        self.sample_question = "What is the capital of France?"

    def test_handle_rate_limit_errors(self):
        func = MagicMock(return_value="value")
        result = projectgpt.handle_rate_limit_errors(func)
        func.assert_called_once()
        self.assertEqual(result, "value")

    def test_create_chat_completion(self):
        with patch("openai.ChatCompletion.create") as mock_create:
            projectgpt.create_chat_completion("System prompt", "User prompt")
        mock_create.assert_called_once()

    def test_answer_question_direct(self):
        with patch("projectgpt.handle_rate_limit_errors") as mock_handle_rate_limit_errors:
            projectgpt.answer_question(self.sample_question, "direct")
        mock_handle_rate_limit_errors.assert_called_once()

    def test_answer_question_projectgpt(self):
        with patch("projectgpt.classify_question") as mock_classify_question, \
                patch("projectgpt.consult_smes") as mock_consult_smes, \
                patch("projectgpt.resolve_best_answer") as mock_resolve_best_answer:
            projectgpt.answer_question(self.sample_question, "projectgpt")
        mock_classify_question.assert_called_once()
        mock_consult_smes.assert_called_once()
        mock_resolve_best_answer.assert_called_once()

    def test_classify_question(self):
        with patch("projectgpt.handle_rate_limit_errors") as mock_handle_rate_limit_errors:
            mock_handle_rate_limit_errors.return_value = MagicMock(
                choices=[
                    MagicMock(
                        message={
                            "content": '{"smes": ["SME1", "SME2", "SME3"]}'
                        }
                    )
                ]
            )
            projectgpt.classify_question(self.sample_question)
        mock_handle_rate_limit_errors.assert_called_once()

    def test_consult_sme(self):
        with patch("projectgpt.handle_rate_limit_errors") as mock_handle_rate_limit_errors:
            projectgpt.consult_sme("SME", self.sample_question)
        mock_handle_rate_limit_errors.assert_called_once()

    def test_consult_smes(self):
        with patch("projectgpt.ThreadPoolExecutor") as mock_executor:
            projectgpt.consult_smes(self.sample_question, ["SME1", "SME2"])
        mock_executor.assert_called_once()

    def test_resolve_best_answer(self):
        answers = {
            "SME1": "Answer 1",
            "SME2": "Answer 2",
        }
        with patch("projectgpt.handle_rate_limit_errors") as mock_handle_rate_limit_errors:
            projectgpt.resolve_best_answer(self.sample_question, answers)
        mock_handle_rate_limit_errors.assert_called_once()

if __name__ == '__main__':
    unittest.main()