""" Unit Test of Main Class """

import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import jinja2

from action.main import Main


class TestMain(unittest.TestCase):
    """Unit Test of Main Class"""

    def setUp(self):
        try:
            os.remove("test.txt")
            os.remove("test.txt.j2")
        except OSError:
            pass

    def test_init_env_var_by_key(self):
        """
        Main.__init__ unittest: Check if environment variable are added in section env
        """
        os.environ["TEST"] = "myfakevalue"
        m = Main()
        self.assertTrue({"TEST": "myfakevalue"}.items() <= m.data["env"].items())
        del os.environ["TEST"]

    def test_init_env_var_by_method(self):
        """
        Main.__init__ unittest: Check if environment variable are availabel with the environ method
        """
        os.environ["TEST"] = "myfakevalue"
        with open("test.txt.j2", "w", encoding="utf-8") as out:
            out.write("{{ environ('TEST') }}")
            out.flush()

        m = Main()
        m.render_file("test.txt.j2")

        self.assertTrue({"TEST": "myfakevalue"}.items() <= m.data["env"].items())
        del os.environ["TEST"]
        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test.txt.j2"), "Original File is deleted")
        with open("test.txt", encoding="utf-8") as f:
            result = f.read()
        self.assertEqual(result, "myfakevalue", "envion method is managed")
        os.remove("test.txt")

    def test_init_undefined_behaviour_ok(self):
        """
        Main.__init__ unittest: Check if all jinja2 undefined behavior are managed
        """
        Main(undefined="Undefined")
        Main(undefined="ChainableUndefined")
        Main(undefined="DebugUndefined")
        Main(undefined="StrictUndefined")

    def test_init_undefined_behaviour_unknow(self):
        """
        Main.__init__ unittest: Check if an unknow jinja2 undefined behavior is in error
        """
        with self.assertRaises(ValueError):
            Main(undefined="Joke")

    def test_add_variables_one_variable(self):
        """
        Main.addVariables unittest: Check if one variable can be added
        """
        m = Main()
        m.add_variables("TEST=toto")
        self.assertTrue({"TEST": "toto"}.items() <= m.data.items())

    def test_add_variables_multiple_variable(self):
        """
        Main.addVariables unittest: Check if multiple variables can be added
        """
        m = Main()
        m.add_variables(
            """
            TEST1=tata
            TEST2=titi
            """
        )
        self.assertTrue({"TEST1": "tata", "TEST2": "titi"}.items() <= m.data.items())

    def test_add_json_section_string_value(self):
        """
        Main.addJsonSection unittest: Check if the section with a
        string value is correctly added to data.
        """
        m = Main()
        m.add_json_section(
            "my_test_section",
            '{"TEST1": "tata", "TEST2": "titi", "problematic-key": "value"}',
        )
        self.assertTrue(
            {
                "my_test_section": {
                    "TEST1": "tata",
                    "TEST2": "titi",
                    "problematic_key": "value",
                }
            }.items()
            <= m.data.items()
        )

    def test_add_json_section_dict_value(self):
        """
        Main.addJsonSection unittest: Check if the section with a
        dict value is correctly added to data.
        """
        m = Main()
        m.add_json_section(
            "my_test_section",
            {"TEST1": "tata", "TEST2": "titi", "problematic-key": "value"},
        )
        self.assertTrue(
            {
                "my_test_section": {
                    "TEST1": "tata",
                    "TEST2": "titi",
                    "problematic_key": "value",
                }
            }.items()
            <= m.data.items()
        )

    @patch("action.main.FileParser", spec=True)
    def test_add_data_file(self, parser_mock):
        """
        Main.addDataFile unittest: Check that Parser class is inialized,
        used to parse then returned dict added to global data.
        """
        # Get the mock instance for Parser
        mock_instance = parser_mock.return_value
        mock_instance.parse = MagicMock(return_value={"TEST": "toto"})

        m = Main()
        m.add_data_file("file_path", "my_format")

        parser_mock.assert_called_with("file_path", "my_format")
        self.assertTrue(mock_instance.parse.called, "parse is called")
        self.assertTrue({"TEST": "toto"}.items() <= m.data.items())

    @patch("action.main.UrlParser", spec=True)
    def test_add_data_url(self, parser_mock):
        """
        Main.test_addDataUrl unittest: Check that Parser class is inialized,
        used to parse then returned dict added to global data.
        """
        # Get the mock instance for Parser
        mock_instance = parser_mock.return_value
        mock_instance.parse = MagicMock(return_value={"TEST": "toto"})

        m = Main()
        m.add_data_url("url", "my_format")

        parser_mock.assert_called_with("url", "my_format")
        self.assertTrue(mock_instance.parse.called, "parse is called")
        self.assertTrue({"TEST": "toto"}.items() <= m.data.items())

    def test_render_file_jinja2(self):
        """
        Main.renderFile unittest: Check if file is rendered by jinja 2 and orginal file removed.
        """
        with open("test.txt.j2", "w", encoding="utf-8") as out:
            out.write("{{ TEST1 }}\n{{ TEST2 }}")
            out.flush()

        m = Main()
        m.data = {"TEST1": "tata", "TEST2": "titi"}
        m.render_file("test.txt.j2")

        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test.txt.j2"), "Original File is deleted")
        with open("test.txt", encoding="utf-8") as f:
            result = f.read()
        self.assertEqual(result, "tata\ntiti", "Template file is managed")
        os.remove("test.txt")

    def test_render_file_keep_file(self):
        """
        Main.renderFile unittest: Check if orginal file can be keeped
        """
        open("test.txt.j2", "a", encoding="utf-8").close()  # pylint: disable=R1732

        m = Main(keep_template=True)
        m.render_file("test.txt.j2")

        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test.txt.j2"), "Original File is NOT deleted")
        os.remove("test.txt")
        os.remove("test.txt.j2")

    def test_render_file_undefined_behaviour(self):
        """
        Main.renderFile unittest: Check if undefined behaviour can be defined
        """
        with open("test.txt.j2", "w", encoding="utf-8") as out:
            out.write("{{ TEST1 }}\n{{ TEST2.f }}\n\n")
            out.flush()
        data = {"TEST1": "tata"}

        m1 = Main()
        m1.data = data
        with self.assertRaises(jinja2.exceptions.UndefinedError):
            m1.render_file("test.txt.j2")

        m2 = Main(undefined="ChainableUndefined")
        m2.data = data
        m2.render_file("test.txt.j2")
        with open("test.txt", encoding="utf-8") as f:
            result = f.read()
        self.assertEqual(
            result, "tata\n\n", "ChainableUndefined behavior was taken in account"
        )
        os.remove("test.txt")

    def test_render_all(self):
        """
        Main.renderAll unittest: Check if multiple file are managed
        """
        open("test1.txt.j2", "a", encoding="utf-8").close()  # pylint: disable=R1732
        open("test2.txt.j2", "a", encoding="utf-8").close()  # pylint: disable=R1732
        Path(".test/directory").mkdir(parents=True, exist_ok=True)
        open(  # pylint: disable=R1732
            ".test/directory/test3.txt.j2", "a", encoding="utf-8"
        ).close()

        m = Main()
        m.render_all()

        self.assertTrue(os.path.isfile("test1.txt"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test2.txt"), "Template file is renamed")
        self.assertTrue(
            os.path.isfile(".test/directory/test3.txt"), "Template file is renamed"
        )

        self.assertFalse(os.path.isfile("test1.txt.j2"), "Original File is deleted")
        self.assertFalse(os.path.isfile("test2.txt.j2"), "Original File is deleted")
        self.assertFalse(
            os.path.isfile(".test/directory/test3.txt.j2"), "Original File is deleted"
        )

        os.remove("test1.txt")
        os.remove("test2.txt")
        shutil.rmtree(".test")
