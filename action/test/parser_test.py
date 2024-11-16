"""
Unit Test of Parser Module
"""

# pylint: disable=W0212

import os
import unittest

from parameterized import parameterized

from action.parser import FileParser, Parser, UrlParser


class TestParser(unittest.TestCase):
    """Unit test of Parser Class"""

    class StubParser(Parser):
        """Stub of a Parser Child Class"""

        def __init__(self, parsed_format=None):
            super().__init__(parsed_format)

        def load(self):
            return "CONTENT_TO_PARSE"

    @parameterized.expand([("ini"), ("json"), ("yaml"), ("yml"), ("env")])
    def test_init_with_managed_format(self, parsed_format):
        """
        Parser.__init__ unittest: Init with managed file format is successfull.
        File format: : ini, json, yaml, yml, env.
        """
        p = TestParser.StubParser(parsed_format)
        self.assertTrue(p.format == parsed_format, "format is stored")

    def test_init_with_unmanaged_format(self):
        """
        Parser.__init__ unittest: Parse with defined unmanaged file format raise exception.
        """
        with self.assertRaises(ValueError):
            TestParser.StubParser("strange_format")

    @parameterized.expand(
        [
            ("ini", "action.parser.Parser._parse_ini"),
            ("json", "action.parser.Parser._parse_json"),
            ("yaml", "action.parser.Parser._parse_yaml"),
            ("yml", "action.parser.Parser._parse_yaml"),
            ("env", "action.parser.Parser._parse_env"),
        ]
    )
    def test_parse_call_correct_parser(self, parsed_format, method):
        """
        Parser.parse unittest: Parse with a preconfigured format must
        load the content and call directly the dedicated parser.
        Test Data:
        | Format | Waited Parser |
        | ----   | ------------ |
        | ini    | action.parser.Parser._parse_ini |
        | json   | action.parser.Parser._parse_json |
        | yaml   | action.parser.Parser._parse_yaml |
        | yml    | action.parser.Parser._parse_yaml |
        | env    | action.parser.Parser._parse_env |
        """
        p = TestParser.StubParser(parsed_format)
        with unittest.mock.patch(method, return_value="fake") as mock:
            ret = p.parse()
            self.assertTrue(mock.called, f"{method} is called")
            mock.assert_called_with("CONTENT_TO_PARSE")
            self.assertTrue(ret == "fake")

    def test_parse_call_unknow_parser(self):
        """
        Parser.parse unittest: Parse with a format not defined
        must call directly the generic parser.
        """
        p = TestParser.StubParser()
        with unittest.mock.patch(
            "action.parser.Parser._parse_generic", return_value="fake"
        ) as mock:
            ret = p.parse()
            self.assertTrue(
                mock.called, "action.parser.Parser._parse_generic is called"
            )
            mock.assert_called_with("CONTENT_TO_PARSE")
            self.assertTrue(ret == "fake")

    def test_parse_ini(self):
        """
        Parser._parse_ini unittest: Parse INI content is successfull.
        """
        ini_content = """
        [exemple]
        TEST1 = tata
        TEST2 = titi
        """
        ret = TestParser.StubParser._parse_ini(ini_content)
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_json(self):
        """
        Parser._parse_json unittest: Parse JSON content is successfull.
        """
        json_content = '{"exemple": {"TEST1": "tata", "TEST2": "titi"}}'
        ret = TestParser.StubParser._parse_json(json_content)
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_yaml(self):
        """
        Parser._parse_yaml unittest: Parse YAML content is successfull.
        """
        yaml_content = """
        exemple:
            TEST1: tata
            TEST2: titi
        """
        ret = TestParser.StubParser._parse_yaml(yaml_content)
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_env(self):
        """
        Parser._parse_env unittest: Parse ENV content is successfull.
        """
        env_content = """
        TEST1=tata
        TEST2=titi
        """
        ret = TestParser.StubParser._parse_env(env_content)
        self.assertEqual({"TEST1": "tata", "TEST2": "titi"}.items(), ret.items())

    def test_parse_generic_ini(self):
        """
        Parser._parse_generic unittest: Generic Parser recognize INI content and parse it.
        """
        ini_content = """
        [exemple]
        TEST1 = tata
        TEST2 = titi
        """
        test_format, ret = TestParser.StubParser._parse_generic(ini_content)
        self.assertEqual(test_format, "ini")
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_generic_json(self):
        """
        Parser._parse_generic unittest: Generic Parser recognize JSON content and parse it.
        """
        json_content = '{"exemple": {"TEST1": "tata", "TEST2": "titi"}}'
        test_format, ret = TestParser.StubParser._parse_generic(json_content)
        self.assertEqual(test_format, "json")
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_generic_yaml(self):
        """
        Parser._parse_generic unittest: Generic Parser parse recognize YAML content and parse it.
        """
        yaml_content = """
        exemple:
            TEST1: tata
            TEST2: titi
        """
        test_format, ret = TestParser.StubParser._parse_generic(yaml_content)
        self.assertEqual(test_format, "yaml")
        self.assertEqual(
            {"exemple": {"TEST1": "tata", "TEST2": "titi"}}.items(), ret.items()
        )

    def test_parse_generic_env(self):
        """
        Parser._parse_generic unittest: Generic Parser parse recognize ENV content and parse it.
        """
        env_content = """
        TEST1=tata
        TEST2=titi
        """
        test_format, ret = TestParser.StubParser._parse_generic(env_content)
        self.assertEqual(test_format, "env")
        self.assertEqual({"TEST1": "tata", "TEST2": "titi"}.items(), ret.items())

    def test_parse_generic_not_managed(self):
        """
        Parser._parse_generic unittest: Generic Parser does"nt recognize/parse unformatted content.
        """
        unknow_content = "asd : fgh : ghj"
        with self.assertRaises(ValueError):
            TestParser.StubParser._parse_generic(unknow_content)


class TestFileParser(unittest.TestCase):
    """Unit Test of FileParse Class"""

    @parameterized.expand([("ini"), ("json"), ("yaml"), ("yml"), ("env")])
    def test_init_with_managed_format(self, test_format):
        """
        FileParser.__init__ unittest: Init with managed file
        format stores the file path and is successfull.
        File format: : ini, json, yaml, yml, env.
        """
        p = FileParser("file_path", test_format)
        self.assertEqual(
            p.file_path, "file_path", "Init store file path without any check"
        )
        self.assertTrue(p.format == test_format, "init stores correct format")

    def test_init_with_unmanaged_format(self):
        """
        FileParser.__init__ unittest: Init with defined unmanaged file format raise exception.
        """
        with self.assertRaises(ValueError):
            FileParser("file_path", "strange_format")

    def test_load_with_predefinedformat(self):
        """
        FileParser.load unittest: Load file wih a predefined format,
        return the file content and keep the format.
        """
        with open("test.txt", "w", encoding="utf-8") as file:
            file.write("CONTENT_TO_PARSE")

        p = FileParser("test.txt", "json")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        self.assertEqual(
            p.format, "json", "Load keeps the predefined format whatever the content"
        )

        os.remove("test.txt")

    @parameterized.expand([("ini"), ("json"), ("yaml"), ("yml"), ("env")])
    def test_load_with_format_found_in_extension(self, extension):
        """
        FileParser.load unittest: Load file wihout predefined format but with a managed
        extension, return the file content and found the format from extension.
        Possible extension: : ini, json, yaml, yml, env.
        """
        with open(f"file_path.{extension}", "w", encoding="utf-8") as file:
            file.write("CONTENT_TO_PARSE")

        p = FileParser(f"file_path.{extension}")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        self.assertTrue(
            p.format == extension, "Load found the format from the extension"
        )

        os.remove(f"file_path.{extension}")


class TestUrlParser(unittest.TestCase):
    """UnitTest of UrlParser Class"""

    @parameterized.expand([("ini"), ("json"), ("yaml"), ("yml"), ("env")])
    def test_init_with_managed_format(self, test_format):
        """
        UrlParser.__init__ unittest: Init with managed file
        format stores the url and is successfull.
        File format: : ini, json, yaml, yml, env.
        """
        p = UrlParser("url", test_format)
        self.assertEqual(p.url, "url", "Init store url without any check")
        self.assertTrue(p.format == test_format, "init stores correct format")

    def test_init_with_unmanaged_format(self):
        """
        UrlParser.__init__ unittest: Init with defined unmanaged format raise exception.
        """
        with self.assertRaises(ValueError):
            UrlParser("url", "strange_format")

    @unittest.mock.patch("urllib.request.urlopen")
    def test_load_with_predefinedformat(self, mock_urlopen):
        """
        UrlParser.load unittest: Load file wih a predefined format,
        return the file content and keep the format.
        """
        cm = unittest.mock.MagicMock()
        cm.read.return_value = "CONTENT_TO_PARSE"
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        p = UrlParser("url", "json")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        self.assertEqual(
            p.format, "json", "Load keeps the predefined format whatever the content"
        )
        cm.getheader.assert_called_with("content-type")

    @parameterized.expand(
        [
            ("application/json", "json"),
            ("text/json", "json"),
            ("application/yaml", "yaml"),
            ("application/x-yaml", "yaml"),
            ("text/x-yaml", "yaml"),
            ("text/yaml", "yaml"),
        ]
    )
    @unittest.mock.patch("urllib.request.urlopen")
    def test_load_with_format_found_in_extension(
        self, content_type, waited_format, mock_urlopen
    ):
        """
        UrlParser.load unittest: Load content wihout predefined format but with a managed http
        return, return the url content and found the format from http header content-type.
        Possible content_type: : ini, json, yaml, yml, env.
        """
        cm = unittest.mock.MagicMock()
        cm.getheader.return_value = content_type
        cm.read.return_value = "CONTENT_TO_PARSE"
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        p = UrlParser("url")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        cm.getheader.assert_called_with("content-type")
        self.assertEqual(
            p.format, waited_format, "Load found the format from the http header"
        )
