import unittest
from benchmark import benchmark
import json
from unittest.mock import patch

class TestBenchmark(unittest.TestCase):

    def test_load_tasks(self):
        tasks_mock = {
            "tasks": [
                {
                    "subject": "Geography",
                    "question": "What is the capital of France?",
                    "options": ["A. Paris", "B. London", "C. Madrid"],
                    "correct_option_index": 0,
                }
            ]
        }
        with patch("builtins.open", unittest.mock.mock_open(read_data=json.dumps(tasks_mock))):
            tasks = benchmark.load_tasks()
        self.assertEqual(tasks, tasks_mock["tasks"])

    def test_format_question(self):
        task = {
            "subject": "Geography",
            "question": "What is the capital of France?",
            "options": ["A. Paris", "B. London", "C. Madrid"],
            "correct_option_index": 0,
        }
        formatted_question = benchmark.format_question(task)
        expected_question = (
            "The following are multiple choice questions (with answers) about Geography.\n"
            "What is the capital of France?\n"
            "Choices:\n"
            "A. Paris\n"
            "B. London\n"
            "C. Madrid\n"
            "Please select only one correct answer without providing any explanation. "
            "To submit your response, simply print the chosen option. Answer: "
        )
        self.assertEqual(formatted_question, expected_question)

    def test_get_answer(self):
        with patch("projectgpt.projectgpt.answer_question") as mock_answer_question:
            benchmark.get_answer("question", "mode")
        mock_answer_question.assert_called_once()

    def test_main(self):
        with patch("benchmark.benchmark.load_dotenv") as mock_load_dotenv, \
            patch("benchmark.benchmark.load_tasks", return_value=[{
                "subject": "Geography",
                "question": "What is the capital of France?",
                "options": ["A. Paris", "B. London", "C. Madrid"],
                "correct_option_index": 0,
            }]) as mock_load_tasks, \
            patch("benchmark.benchmark.format_question") as mock_format_question, \
            patch("benchmark.benchmark.get_answer", return_value=("A. Paris", 1)) as mock_get_answer, \
            patch("builtins.open", unittest.mock.mock_open()):
            benchmark.main()
        mock_load_dotenv.assert_called_once()
        mock_load_tasks.assert_called_once()
        mock_format_question.assert_called()
        mock_get_answer.assert_called()

if __name__ == '__main__':
    unittest.main()