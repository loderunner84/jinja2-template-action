import unittest
from action.main import Main
import shutil
import os
import subprocess

class TestStringMethods(unittest.TestCase):

    def test_renderFile(self):
        os.environ["TEST"] = "toto"

        m = Main()
        self.assertFalse(os.path.isfile("test/template"), "New File does not exist before")
        m.renderFile("test/template.j2")
        self.assertTrue(os.path.isfile("test/template"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test/template.j2"), "Original File is deleted")
        with open("test/template") as f:
            s = f.read()
        self.assertEqual(s, "toto", "Template file is managed")
        os.remove("test/template")
        subprocess.run("git restore test/template.j2", shell = True, executable="/bin/bash")

    def test_renderAll(self):
        os.environ["TEST"] = "toto"

        m = Main()
        self.assertFalse(os.path.isfile("test/template"), "New File does not exist before")
        m.renderAll()
        self.assertTrue(os.path.isfile("test/template"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test/template.j2"), "Original File is deleted")
        with open("test/template") as f:
            s = f.read()
        self.assertEqual(s, "toto", "Template file is managed")
        os.remove("test/template")
        subprocess.run("git restore test/template.j2", shell = True, executable="/bin/bash")


if __name__ == '__main__':
    unittest.main()