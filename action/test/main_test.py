import unittest
from unittest.mock import patch, MagicMock
from action.main import Main
import shutil
import os
from pathlib import Path
import subprocess

class TestMain(unittest.TestCase):

    def setUp(self):
        try:
            os.remove("test.txt")
            os.remove("test.txt.j2")
        except OSError:
            pass

    def test_init_env_var_by_key(self):
        '''
        Main.__init__ unittest: Check if environment variable are added in section env
        '''
        os.environ["TEST"] = "myfakevalue"
        m = Main()
        self.assertTrue({'TEST': 'myfakevalue'}.items() <= m.data['env'].items())
        del os.environ['TEST']

    def test_init_env_var_by_method(self):
        '''
        Main.__init__ unittest: Check if environment variable are availabel with the environ method
        '''
        os.environ["TEST"] = "myfakevalue"
        with open("test.txt.j2", 'w') as out:
            out.write("{{ environ('TEST') }}")
            out.flush()
        
        m = Main()
        m.renderFile("test.txt.j2")

        self.assertTrue({'TEST': 'myfakevalue'}.items() <= m.data['env'].items())
        del os.environ['TEST']
        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test.txt.j2"), "Original File is deleted")
        with open("test.txt") as f:
            result = f.read()
        self.assertEqual(result, "myfakevalue", "envion method is managed")
        os.remove("test.txt")

    def test_addVariables_oneVariable(self):
        '''
        Main.addVariables unittest: Check if one variable can be added
        '''
        m = Main()
        m.addVariables("TEST=toto")
        self.assertTrue({'TEST': 'toto'}.items() <= m.data.items())

    def test_addVariables_multipleVariable(self):
        '''
        Main.addVariables unittest: Check if multiple variables can be added
        '''
        m = Main()
        m.addVariables("""
            TEST1=tata
            TEST2=titi
        """)
        self.assertTrue({'TEST1': 'tata', 'TEST2': 'titi'}.items() <= m.data.items())

    def test_addJsonSection_stringValue(self):
        '''
        Main.addJsonSection unittest: Check if the section with a string value is correctly added to data.
        '''
        m = Main()
        m.addJsonSection("my_test_section", "{\"TEST1\": \"tata\", \"TEST2\": \"titi\", \"problematic-key\": \"value\"}")
        self.assertTrue({'my_test_section': {'TEST1': 'tata', 'TEST2': 'titi', 'problematic_key': 'value' }}.items() <= m.data.items())

    def test_addJsonSection_dictValue(self):
        '''
        Main.addJsonSection unittest: Check if the section with a dict value is correctly added to data.
        '''
        m = Main()
        m.addJsonSection("my_test_section", {'TEST1': 'tata', 'TEST2': 'titi', 'problematic-key': 'value'})
        self.assertTrue({'my_test_section': {'TEST1': 'tata', 'TEST2': 'titi', 'problematic_key': 'value'}}.items() <= m.data.items())

    @patch('action.main.Parser', spec=True)
    def test_addDataFile(self, ParserMock):
        '''
        Main.addDataFile unittest: Check that Parser class is inialized, used to parse then returned dict added to global data.
        '''
        # Get the mock instance for Parser
        mock_instance = ParserMock.return_value
        mock_instance.parse = MagicMock(return_value={'TEST': 'toto'})

        m = Main()
        m.addDataFile("file_path", "my_format")
        print(ParserMock.mock_calls)

        ParserMock.assert_called_with("file_path", "my_format")
        self.assertTrue(mock_instance.parse.called, "parse is called")
        self.assertTrue({'TEST': 'toto'}.items() <= m.data.items())

    def test_renderFile_jinja2(self):
        '''
        Main.renderFile unittest: Check if file is rendered by jinja 2 and orginal file removed.
        '''
        with open("test.txt.j2", 'w') as out:
            out.write("{{ TEST1 }}\n{{ TEST2 }}")
            out.flush()
        
        m = Main()
        m.data = {'TEST1': 'tata', 'TEST2': 'titi'}
        m.renderFile("test.txt.j2")
        
        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test.txt.j2"), "Original File is deleted")
        with open("test.txt") as f:
            result = f.read()
        self.assertEqual(result, "tata\ntiti", "Template file is managed")
        os.remove("test.txt")

    def test_renderFile_keep_file(self):
        '''
        Main.renderFile unittest: Check if orginal file can be keeped
        '''
        open("test.txt.j2", 'a').close()
        
        m = Main(keep_template=True)
        m.renderFile("test.txt.j2")

        self.assertTrue(os.path.isfile("test.txt"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test.txt.j2"), "Original File is NOT deleted")
        os.remove("test.txt")
        os.remove("test.txt.j2")

    def test_renderAll(self):
        '''
        Main.renderAll unittest: Check if multiple file are managed
        '''
        open("test1.txt.j2", 'a').close()
        open("test2.txt.j2", 'a').close()
        Path(".test/directory").mkdir(parents=True, exist_ok=True)
        open(".test/directory/test3.txt.j2", 'a').close()
        
        m = Main()
        m.renderAll()
        
        self.assertTrue(os.path.isfile("test1.txt"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test2.txt"), "Template file is renamed")
        self.assertTrue(os.path.isfile(".test/directory/test3.txt"), "Template file is renamed")

        self.assertFalse(os.path.isfile("test1.txt.j2"), "Original File is deleted")
        self.assertFalse(os.path.isfile("test2.txt.j2"), "Original File is deleted")
        self.assertFalse(os.path.isfile(".test/directory/test3.txt.j2"), "Original File is deleted")
        
        os.remove("test1.txt")
        os.remove("test2.txt")
        shutil.rmtree(".test")
