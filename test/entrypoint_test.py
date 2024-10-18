import unittest
import os
from unittest.mock import patch
from unittest.mock import MagicMock
from click.testing import CliRunner
from entrypoint import main
from action.main import Main


class TestEntrypoint(unittest.TestCase):
    
    @patch('entrypoint.Main', spec=True)
    def test_main_noEnvVar(self, MainClassMock):
        # Get the mock instance for MainClassMock
        mock_instance = MainClassMock.return_value
        # Ensure No INPUT_VARIABLES Defined
        os.environ.pop('INPUT_VARIABLES', None)

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        self.assertFalse(mock_instance.addVariables.called, "addVariables is not called")
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")

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
        # Add Some Content in the specific INPUT_VARIABLES env car
        os.environ['INPUT_VARIABLES'] = "test_content"

        # Call the Method (click)
        runner = CliRunner()
        result = runner.invoke(main)

        mock_instance.addVariables.assert_called_with("test_content")
        self.assertTrue(mock_instance.renderAll.called, "renderAll is called")