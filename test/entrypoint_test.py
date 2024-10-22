import unittest
import os
from unittest.mock import patch, call
from unittest.mock import MagicMock
from click.testing import CliRunner
from entrypoint import main
from action.main import Main


class TestEntrypoint(unittest.TestCase):
    '''
    entrypoint.py Unit Test.
    
    This test the link between cli argument/env. var. and 
    how Main class is instancied.
    '''
    
    @patch('entrypoint.Main', spec=True)
    def test_main_keepTemplate(self, MainClassMock):
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value

        # Call the Method with keep_template
        runner = CliRunner()
        result = runner.invoke(main, ['--keep_template'])
      
        #print(MainClassMock.call_args.kwargs.get('keep_template'))
        self.assertTrue(MainClassMock.call_args.kwargs.get('keep_template'))

        # Call the Method without keep_template
        result = runner.invoke(main)
        self.assertFalse(MainClassMock.call_args.kwargs.get('keep_template'))
    
    @patch('entrypoint.Main', spec=True)
    def test_main_envVar(self, MainClassMock):
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value
        # Add Some Content in a env file
        with open("test.txt", 'w') as out:
            out.write("test_content")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main, [f"--var_file=test.txt"])

        mock_instance.addVariables.assert_called_with("test_content")
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

        # Remove the previous call
        mock_instance.addVariables.reset_mock()
        os.remove("test.txt")

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        self.assertTrue(
            call("test_content") not in mock_instance.addVariables.mock_calls,
            f"addVariables is not called"
        )

    @patch('entrypoint.Main', spec=True)
    def test_main_context_one(self, MainClassMock):
        '''
        '''
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value
        # Add Some Content in a context file
        with open("my_context.txt", 'w') as out:
            out.write("test_content")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main, [f"--context=my_context.txt"])

        mock_instance.addJsonSection.assert_called_with("my_context", "test_content")
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

        # Remove the previous env var
        mock_instance.addJsonSection.reset_mock()
        os.remove("my_context.txt")

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        self.assertTrue(
            call("my_context", "test_content") not in mock_instance.addJsonSection.mock_calls,
            f"addJsonSection is not called for the previous context"
        )
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

    @patch('entrypoint.Main', spec=True)
    def test_main_context_multiple(self, MainClassMock):
        '''
        '''
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value
        # Add Some Content in a context file
        with open("my_context1.txt", 'w') as out:
            out.write("this is")
            out.flush()
        with open("my_context2.txt", 'w') as out:
            out.write("so funny")
            out.flush()

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main, ["--context=my_context1.txt", "--context=my_context2.txt"])

        # Test
        calls = [call("my_context1", "this is"), call("my_context2", "so funny")]
        mock_instance.addJsonSection.assert_has_calls(calls, any_order=True)
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

        # Clean
        os.remove("my_context1.txt")
        os.remove("my_context2.txt")

    @patch('entrypoint.Main', spec=True)
    def test_main_data_file_no_format(self, MainClassMock):
        '''
        entrypoint.main unittest: If data_file parameter is defined, addDataFile method is called with the file path.
        '''
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main, [f"--data_file=my_file.json"])

        mock_instance.addJsonSection.addDataFile("my_file.json", None)
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

        # Remove the previous env var
        mock_instance.addJsonSection.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        self.assertTrue(
            call("my_file.json", None) not in mock_instance.addJsonSection.mock_calls,
            f"addDataFile is not called for the previous context"
        )
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

    @patch('entrypoint.Main', spec=True)
    def test_main_data_file_with_format(self, MainClassMock):
        '''
        entrypoint.main unittest: If data_file parameter and data_format are defined, addDataFile method is called with the file path and the format.
        '''
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main, [f"--data_file=my_file.json --data_format=my_format"])

        mock_instance.addJsonSection.addDataFile("my_file.json", "my_format")
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

        # Remove the previous env var
        mock_instance.addJsonSection.reset_mock()

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        self.assertTrue(
            call("my_file.json", "my_format") not in mock_instance.addJsonSection.mock_calls,
            f"addDataFile is not called for the previous context"
        )
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")