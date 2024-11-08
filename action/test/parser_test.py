import os
import unittest
from parameterized import parameterized
from action.parser import FileParser, Parser

class TestParser(unittest.TestCase):
    
    class StubParser(Parser):
        def __init__(self, format=None):       
            super().__init__(format)

        def load(self):
            return "CONTENT_TO_PARSE"
    
    @parameterized.expand([
        ('ini'),
        ('json'),
        ('yaml'),
        ('yml'),
        ('env')
    ])
    def test_init_with_managed_format(self, format):
        '''
        Parser.__init__ unittest: Init with managed file format is successfull.
        File format: : ini, json, yaml, yml, env.
        '''
        p = TestParser.StubParser(format)
        self.assertTrue(p.format == format, "format is stored")

    def test_init_with_unmanaged_format(self):
        '''
        Parser.__init__ unittest: Parse with defined unmanaged file format raise exception.
        '''
        with self.assertRaises(ValueError):
            p = TestParser.StubParser("strange_format")

    @parameterized.expand([
        ('ini', 'action.parser.Parser._parse_ini'),
        ('json', 'action.parser.Parser._parse_json'),
        ('yaml', 'action.parser.Parser._parse_yaml'),
        ('yml', 'action.parser.Parser._parse_yaml'),
        ('env', 'action.parser.Parser._parse_env')
    ])
    def test_parse_call_correct_parser(self, format, method):
        '''
        Parser.parse unittest: Parse with a preconfigured format must load the content and call directly the dedicated parser.
        Test Data:
        | Format | Waited Parser |
        | ----   | ------------ |
        | ini    | action.parser.Parser._parse_ini |
        | json   | action.parser.Parser._parse_json |
        | yaml   | action.parser.Parser._parse_yaml |
        | yml    | action.parser.Parser._parse_yaml |
        | env    | action.parser.Parser._parse_env |
        '''
        p = TestParser.StubParser(format)
        with unittest.mock.patch(method, return_value="fake") as mock :
            ret = p.parse()
            self.assertTrue(mock.called, f"{method} is called")
            mock.assert_called_with("CONTENT_TO_PARSE")
            self.assertTrue(ret == "fake")

    def test_parse_call_unknow_parser(self):
        '''
        Parser.parse unittest: Parse with a format not defined must call directly the generic parser.
        '''        
        p = TestParser.StubParser()
        with unittest.mock.patch('action.parser.Parser._parse_generic', return_value="fake") as mock :
            ret = p.parse()
            self.assertTrue(mock.called, f"action.parser.Parser._parse_generic is called")
            mock.assert_called_with("CONTENT_TO_PARSE")
            self.assertTrue(ret == "fake")

    def test_parse_ini(self):
        '''
        Parser._parse_ini unittest: Parse INI content is successfull.
        '''
        ini_content="""
        [exemple]
        TEST1 = tata
        TEST2 = titi
        """
        ret = TestParser.StubParser._parse_ini(ini_content)
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_json(self):
        '''
        Parser._parse_json unittest: Parse JSON content is successfull.
        '''
        json_content="{\"exemple\": {\"TEST1\": \"tata\", \"TEST2\": \"titi\"}}"
        ret = TestParser.StubParser._parse_json(json_content)
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_yaml(self):
        '''
        Parser._parse_yaml unittest: Parse YAML content is successfull.
        '''
        yaml_content="""
        exemple:
            TEST1: tata
            TEST2: titi
        """
        ret = TestParser.StubParser._parse_yaml(yaml_content)
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_env(self):
        '''
        Parser._parse_env unittest: Parse ENV content is successfull.
        '''
        env_content="""
        TEST1=tata
        TEST2=titi
        """
        ret = TestParser.StubParser._parse_env(env_content)
        self.assertEqual({'TEST1': 'tata', 'TEST2': 'titi'}.items(), ret.items())

    def test_parse_generic_ini(self):
        '''
        Parser._parse_generic unittest: Generic Parser recognize INI content and parse it.
        '''
        ini_content="""
        [exemple]
        TEST1 = tata
        TEST2 = titi
        """
        format,ret = TestParser.StubParser._parse_generic(ini_content)
        self.assertEqual(format, 'ini')
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_generic_json(self):
        '''
        Parser._parse_generic unittest: Generic Parser recognize JSON content and parse it.
        '''
        json_content="{\"exemple\": {\"TEST1\": \"tata\", \"TEST2\": \"titi\"}}"
        format,ret = TestParser.StubParser._parse_generic(json_content)
        self.assertEqual(format, 'json')
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_generic_yaml(self):
        '''
        Parser._parse_generic unittest: Generic Parser parse recognize YAML content and parse it.
        '''
        yaml_content="""
        exemple:
            TEST1: tata
            TEST2: titi
        """
        format,ret = TestParser.StubParser._parse_generic(yaml_content)
        self.assertEqual(format, 'yaml')
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_generic_env(self):
        '''
        Parser._parse_generic unittest: Generic Parser parse recognize ENV content and parse it.
        '''
        env_content="""
        TEST1=tata
        TEST2=titi
        """
        format,ret = TestParser.StubParser._parse_generic(env_content)
        self.assertEqual(format, 'env')
        self.assertEqual({'TEST1': 'tata', 'TEST2': 'titi'}.items(), ret.items())

    def test_parse_generic_not_managed(self):
        '''
        Parser._parse_generic unittest: Generic Parser does'nt recognize/parse unformatted content.
        '''
        unknow_content='asd : fgh : ghj'
        with self.assertRaises(ValueError):
            format,ret = TestParser.StubParser._parse_generic(unknow_content)


class TestFileParser(unittest.TestCase):

    @parameterized.expand([
        ('ini'),
        ('json'),
        ('yaml'),
        ('yml'),
        ('env')
    ])
    def test_init_with_managed_format(self, format):
        '''
        Parser.__init__ unittest: Init with managed file format stores the file path and is successfull.
        File format: : ini, json, yaml, yml, env.
        '''
        p = FileParser("file_path", format)
        self.assertEqual(p.file_path, "file_path", "Init store file path without any check")
        self.assertTrue(p.format == format, "init stores correct format")

    def test_init_with_unmanaged_format(self):
        '''
        Parser.__init__ unittest: Parse with defined unmanaged file format raise exception.
        '''
        with self.assertRaises(ValueError):
            p = FileParser("file_path", "strange_format")

    def test_load_with_predefinedformat(self):
        '''
        FileParser.load unittest: Load file wih a predefined format, return the file content and keep the format.
        '''
        with open("test.txt", 'w') as file:
            file.write("CONTENT_TO_PARSE")

        p = FileParser("test.txt", "json")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        self.assertEqual(p.format, "json", "Load keeps the predefined format whatever the content")

        os.remove("test.txt")

    @parameterized.expand([
        ('ini'),
        ('json'),
        ('yaml'),
        ('yml'),
        ('env')
    ])
    def test_load_with_format_found_in_extension(self, extension):
        '''
        Parser.load unittest: Load file wihout predefined format but with a managed extension, return the file content and found the format from extension.
        Possible extension: : ini, json, yaml, yml, env.
        '''
        with open(f"file_path.{extension}", 'w') as file:
            file.write("CONTENT_TO_PARSE")

        p = FileParser(f"file_path.{extension}")
        ret = p.load()
        self.assertEqual(ret, "CONTENT_TO_PARSE", "Load return the file content")
        self.assertTrue(p.format == extension, "Load found the format from the extension")

        os.remove(f"file_path.{extension}")


