import os
import argparse
from unittest.mock import patch, MagicMock
import pytest
from cover_agent.main import parse_args, main


class TestMain:
    def test_parse_args(self):
        with patch(
            "sys.argv",
            [
                "program.py",
                "--source-file-path",
                "test_source.py",
                "--test-file-path",
                "test_file.py",
                "--code-coverage-report-path",
                "coverage_report.xml",
                "--test-command",
                "pytest",
            ],
        ):
            args = parse_args()
            assert args.source_file_path == "test_source.py"
            assert args.test_file_path == "test_file.py"
            assert args.code_coverage_report_path == "coverage_report.xml"
            assert args.test_command == "pytest"
            assert args.test_command_dir == os.getcwd()
            assert args.included_files is None
            assert args.coverage_type == "cobertura"
            assert args.report_filepath == "test_results.html"
            assert args.desired_coverage == 90
            assert args.max_iterations == 10

    @patch("cover_agent.main.UnitTestGenerator")
    @patch("cover_agent.main.ReportGenerator")
    @patch("cover_agent.main.os.path.isfile")
    def test_main_source_file_not_found(
        self, mock_isfile, mock_report_generator, mock_unit_cover_agent
    ):
        # Mocking argparse.Namespace object
        args = argparse.Namespace(
            source_file_path="test_source.py",
            test_file_path="test_file.py",
            code_coverage_report_path="coverage_report.xml",
            test_command="pytest",
            test_command_dir=os.getcwd(),
            included_files=None,
            coverage_type="cobertura",
            report_filepath="test_results.html",
            desired_coverage=90,
            max_iterations=10,
        )
        parse_args = lambda: args  # Mocking parse_args function
        mock_isfile.return_value = False  # Simulate source file not found

        with patch("cover_agent.main.parse_args", parse_args):
            with pytest.raises(FileNotFoundError) as exc_info:
                main()

        # Assert that FileNotFoundError was raised with the correct message
        assert (
            str(exc_info.value) == f"Source file not found at {args.source_file_path}"
        )

        # Assert that UnitTestGenerator and ReportGenerator were not called
        mock_unit_cover_agent.assert_not_called()
        mock_report_generator.generate_report.assert_not_called()

    @patch("cover_agent.main.os.path.exists")
    @patch("cover_agent.main.os.path.isfile")
    @patch("cover_agent.main.UnitTestGenerator")
    def test_main_test_file_not_found(
        self, mock_unit_cover_agent, mock_isfile, mock_exists
    ):
        # Mocking argparse.Namespace object
        args = argparse.Namespace(
            source_file_path="test_source.py",
            test_file_path="test_file.py",
            code_coverage_report_path="coverage_report.xml",
            test_command="pytest",
            test_command_dir=os.getcwd(),
            included_files=None,
            coverage_type="cobertura",
            report_filepath="test_results.html",
            desired_coverage=90,
            max_iterations=10,
            prompt_only=False,
        )
        parse_args = lambda: args  # Mocking parse_args function
        mock_isfile.side_effect = [
            True,
            False,
        ]  # Simulate source file exists, test file not found
        mock_exists.return_value = True  # Simulate markdown file exists

        with patch("cover_agent.main.parse_args", parse_args):
            with pytest.raises(FileNotFoundError) as exc_info:
                main()

        # Assert that FileNotFoundError was raised with the correct message
        assert str(exc_info.value) == f"Test file not found at {args.test_file_path}"