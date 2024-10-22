import os
import unittest
from parameterized import parameterized
from action.parser import Parser

class TestParser(unittest.TestCase):

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
        p = Parser("file_path", format)
        self.assertTrue(p.file_format == format, "format is stored")
        self.assertTrue(p.file_path == "file_path", "file_path is stored")

    def test_init_with_unmanaged_format(self):
        '''
        Parser.__init__ unittest: Init with unmanaged file format raise exception.
        File format: : ini, json, yaml, yml, env.
        '''
        with self.assertRaises(ValueError):
            p = Parser("file_path", "strange_format")

    @parameterized.expand([
        ('ini'),
        ('json'),
        ('yaml'),
        ('yml'),
        ('env')
    ])
    def test_init_with_format_found_in_extension(self, extension):
        '''
        Parser.__init__ unittest: Init without format specified but with a official extension defines the format.
        Possible extension: : ini, json, yaml, yml, env.
        '''
        p = Parser(f"file_path.{extension}")
        self.assertTrue(p.file_format == extension, "format is stored")
        self.assertTrue(p.file_path == f"file_path.{extension}", "file_path is stored")

    @parameterized.expand([
        ('ini', 'action.parser.Parser._parse_ini'),
        ('json', 'action.parser.Parser._parse_json'),
        ('yaml', 'action.parser.Parser._parse_yaml'),
        ('yml', 'action.parser.Parser._parse_yaml'),
        ('env', 'action.parser.Parser._parse_env')
    ])
    def test_parse_call_correct_parser(self, format, method):
        '''
        Parser.parse unittest: Parse with a preconfigured format must call directly the dedicated parser.
        Test Data:
        | Format | Waited Parser |
        | ----   | ------------ |
        | ini    | action.parser.Parser._parse_ini |
        | json   | action.parser.Parser._parse_json |
        | yaml   | action.parser.Parser._parse_yaml |
        | yml    | action.parser.Parser._parse_yaml |
        | env    | action.parser.Parser._parse_env |
        '''
        with open("test.txt", 'w') as file:
            file.write("CONTENT_TO_PARSE")
         
        p = Parser("test.txt", format)
        with unittest.mock.patch(method, return_value="fake") as mock :
            ret = p.parse()
            self.assertTrue(mock.called, f"{method} is called")
            mock.assert_called_with("CONTENT_TO_PARSE")
            self.assertTrue(ret == "fake")

        os.remove("test.txt")

    def test_parse_call_unknow_parser(self):
        '''
        Parser.parse unittest: Parse with a unknow format must call directly the generic parser.
        '''
        with open("test.txt", 'w') as file:
            file.write("CONTENT_TO_PARSE")
         
        p = Parser("test.txt")
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
        ret = Parser._parse_ini(ini_content)
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_json(self):
        '''
        Parser._parse_json unittest: Parse JSON content is successfull.
        '''
        json_content="{\"exemple\": {\"TEST1\": \"tata\", \"TEST2\": \"titi\"}}"
        ret = Parser._parse_json(json_content)
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
        ret = Parser._parse_yaml(yaml_content)
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_env(self):
        '''
        Parser._parse_env unittest: Parse ENV content is successfull.
        '''
        env_content="""
        TEST1=tata
        TEST2=titi
        """
        ret = Parser._parse_env(env_content)
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
        format,ret = Parser._parse_generic(ini_content)
        self.assertEqual(format, 'ini')
        self.assertEqual({'exemple': {'TEST1': 'tata', 'TEST2': 'titi'}}.items(), ret.items())

    def test_parse_generic_json(self):
        '''
        Parser._parse_generic unittest: Generic Parser recognize JSON content and parse it.
        '''
        json_content="{\"exemple\": {\"TEST1\": \"tata\", \"TEST2\": \"titi\"}}"
        format,ret = Parser._parse_generic(json_content)
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
        format,ret = Parser._parse_generic(yaml_content)
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
        format,ret = Parser._parse_generic(env_content)
        self.assertEqual(format, 'env')
        self.assertEqual({'TEST1': 'tata', 'TEST2': 'titi'}.items(), ret.items())

    def test_parse_generic_not_managed(self):
        '''
        Parser._parse_generic unittest: Generic Parser does'nt recognize/parse unformatted content.
        '''
        unknow_content='asd : fgh : ghj'
        with self.assertRaises(ValueError):
            format,ret = Parser._parse_generic(unknow_content)

