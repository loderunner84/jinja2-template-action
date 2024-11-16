"""UnitTest entrypoint file"""

import os
import unittest
from unittest.mock import call, patch

from click.testing import CliRunner
from parameterized import parameterized

from entrypoint import main


class TestEntrypoint(unittest.TestCase):
    """
    entrypoint.py Unit Test.
    This test the link between cli argument/env. var. and
    how Main class is instancied.
    """

    @patch("entrypoint.Main", spec=True)
    def test_main_keep_template(self, main_class_mock):
        """
        entrypoint.main unittest: If keep_template option is used on the cli,
        main class must be initialized with the keep_template property to true.
        """
        # Call the Method with keep_template
        runner = CliRunner()
        runner.invoke(main, ["--keep_template"])

        self.assertTrue(main_class_mock.call_args.kwargs.get("keep_template"))

        # Call the Method without keep_template
        runner.invoke(main)
        self.assertFalse(main_class_mock.call_args.kwargs.get("keep_template"))

    @patch("entrypoint.Main", spec=True)
    def test_main_undefined_behaviour(self, main_class_mock):
        """
        entrypoint.main unittest: If undefined_behaviour option is used on the cli,
        main class must be initialized with the given undefined_behaviour if not default
        'Undefined' value must be used.
        """
        # Call the Method with undefined_behaviour
        runner = CliRunner()
        runner.invoke(main, ["--undefined_behaviour=StrangeTest"])

        self.assertEqual(
            "StrangeTest", main_class_mock.call_args.kwargs.get("undefined")
        )

        # Call the Method without keep_template
        runner.invoke(main)
        self.assertEqual("Undefined", main_class_mock.call_args.kwargs.get("undefined"))

    @patch("entrypoint.Main", spec=True)
    def test_main_en_var(self, main_class_mock):
        """
        entrypoint.main unittest: If a var file is given, add_variables
        method is called with the content of that file.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value
        # Add Some Content in a env file
        with open("test.txt", "w", encoding="utf-8") as out:
            out.write("test_content")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--var_file=test.txt"])

        mock_instance.add_variables.assert_called_with("test_content")
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous call
        mock_instance.add_variables.reset_mock()
        os.remove("test.txt")

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("test_content") not in mock_instance.add_variables.mock_calls,
            "add_variables is not called",
        )

    @patch("entrypoint.Main", spec=True)
    def test_main_context_one(self, main_class_mock):
        """
        entrypoint.main unittest: If one context file is given add_json_section
        method is called with its content for the context defiend by the name of the file.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value
        # Add Some Content in a context file
        with open("my_context.txt", "w", encoding="utf-8") as out:
            out.write("test_content")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--context=my_context.txt"])

        mock_instance.add_json_section.assert_called_with("my_context", "test_content")
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous env var
        mock_instance.add_json_section.reset_mock()
        os.remove("my_context.txt")

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("my_context", "test_content")
            not in mock_instance.add_json_section.mock_calls,
            "add_json_section is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

    @parameterized.expand([(""), ("none\n")])
    @patch("entrypoint.Main", spec=True)
    def test_main_context_null(self, content, main_class_mock):
        """
        entrypoint.main unittest: If context file content is empty or
        contains "null\n",add_json_section method is NOT called.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value
        # Add Some Content in a context file
        with open("my_context.txt", "w", encoding="utf-8") as out:
            out.write(content)
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--context=my_context.txt"])

        self.assertTrue(
            call("my_context", "test_content")
            not in mock_instance.add_json_section.mock_calls,
            "add_json_section is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the file
        os.remove("my_context.txt")

    @patch("entrypoint.Main", spec=True)
    def test_main_context_multiple(self, main_class_mock):
        """
        entrypoint.main unittest: If multiple context file is given add_json_section method is
        called with each file content for the each context defined by the name of each file.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value
        # Add Some Content in a context file
        with open("my_context1.txt", "w", encoding="utf-8") as out:
            out.write("this is")
            out.flush()
        with open("my_context2.txt", "w", encoding="utf-8") as out:
            out.write("so funny")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--context=my_context1.txt", "--context=my_context2.txt"])

        # Test
        calls = [call("my_context1", "this is"), call("my_context2", "so funny")]
        mock_instance.add_json_section.assert_has_calls(calls, any_order=True)
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Clean
        os.remove("my_context1.txt")
        os.remove("my_context2.txt")

    @patch("entrypoint.Main", spec=True)
    def test_main_data_file_no_format(self, main_class_mock):
        """
        entrypoint.main unittest: If data_file parameter is defined,
        add_data_file method is called with the file path.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--data_file=my_file.json"])

        mock_instance.add_data_file.assert_called_with("my_file.json", None)
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous env var
        mock_instance.add_data_file.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("my_file.json", None) not in mock_instance.add_data_file.mock_calls,
            "add_data_file is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

    @patch("entrypoint.Main", spec=True)
    def test_main_data_file_with_format(self, main_class_mock):
        """
        entrypoint.main unittest: If data_file parameter and data_format are defined,
        add_data_file method is called with the file path and the format.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--data_file=my_file.json", "--data_format=my_format"])

        mock_instance.add_data_file.assert_called_with("my_file.json", "my_format")
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous env var
        mock_instance.add_data_file.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("my_file.json", "my_format")
            not in mock_instance.add_data_file.mock_calls,
            "add_data_file is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

    @patch("entrypoint.Main", spec=True)
    def test_main_url_file_no_format(self, main_class_mock):
        """
        entrypoint.main unittest: If data_url parameter is defined,
        add_data_url method is called with the url.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--data_url=my_url"])

        mock_instance.add_data_url.assert_called_with("my_url", None)
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous env var
        mock_instance.add_data_url.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("my_url", None) not in mock_instance.add_data_url.mock_calls,
            "add_data_url is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

    @patch("entrypoint.Main", spec=True)
    def test_main_urlfile_with_format(self, main_class_mock):
        """
        entrypoint.main unittest: If data_url parameter and data_url_format
        are defined, add_data_url method is called with the url and the format.
        """
        # Get the mock instance for main_class_mock
        mock_instance = main_class_mock.return_value

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main, ["--data_url=my_url", "--data_url_format=my_format"])

        mock_instance.add_data_url.assert_called_with("my_url", "my_format")
        self.assertTrue(mock_instance.render_all.called, "render_all is called")

        # Remove the previous env var
        mock_instance.add_data_url.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        runner.invoke(main)

        self.assertTrue(
            call("my_url", "my_format") not in mock_instance.add_data_url.mock_calls,
            "add_data_file is not called for the previous context",
        )
        self.assertTrue(mock_instance.render_all.called, "render_all is called")
