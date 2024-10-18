import unittest
from action.main import Main
import shutil
import os
import subprocess

class TestMain(unittest.TestCase):

    def test_addVariables_oneVariable(self):
        m = Main()
        m.addVariables("TEST=toto")
        self.assertTrue(m.data == {'TEST': 'toto'})

    def test_addVariables_multipleVariable(self):
        m = Main()
        m.addVariables("""
            TEST1=tata
            TEST2=titi
        """)
        self.assertTrue(m.data == {'TEST1': 'tata', 'TEST2': 'titi'})

    def test_renderFile_oneEnv(self):
        os.environ["TEST"] = "toto"

        m = Main()
        self.assertFalse(os.path.isfile("test/env-var/template"), "New File does not exist before")
        m.renderFile("test/env-var/template.j2")
        self.assertTrue(os.path.isfile("test/env-var/template"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test/env-var/template.j2"), "Original File is deleted")
        with open("test/env-var/template") as f:
            result = f.read()
        self.assertEqual(result, "toto", "Template file is managed")
        os.remove("test/env-var/template")
        subprocess.run("git restore test/env-var/template.j2", shell = True, executable="/bin/bash")

    def test_renderFile_keep_file(self):
        m = Main(keep_template=True)
        self.assertFalse(os.path.isfile("test/env-var/template"), "New File does not exist before")
        m.renderFile("test/env-var/template.j2")
        self.assertTrue(os.path.isfile("test/env-var/template"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test/env-var/template.j2"), "Original File is NOT deleted")
        os.remove("test/env-var/template")
        subprocess.run("git restore test/env-var/template.j2", shell = True, executable="/bin/bash")

    def test_renderFile_manyVariables(self):
        m = Main()
        m.addVariables("""
            TEST1=tata
            TEST2=titi
        """)
        self.assertFalse(os.path.isfile("test/many-var/template"), "New File does not exist before")
        m.renderFile("test/many-var/template.j2")
        self.assertTrue(os.path.isfile("test/many-var/template"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test/many-var/template.j2"), "Original File is deleted")
        with open("test/many-var/template") as f:
            result = f.read()
        self.assertEqual(result, "tata\ntiti", "Template file is managed")
        os.remove("test/many-var/template")
        subprocess.run("git restore test/many-var/template.j2", shell = True, executable="/bin/bash")

    def test_renderAll(self):
        m = Main()
        self.assertFalse(os.path.isfile("test/env-var/template"), "New File does not exist before")
        self.assertFalse(os.path.isfile("test/many-var/template"), "New File does not exist before")
        m.renderAll()
        self.assertTrue(os.path.isfile("test/env-var/template"), "Template file is renamed")
        self.assertTrue(os.path.isfile("test/many-var/template"), "Template file is renamed")
        self.assertFalse(os.path.isfile("test/env-var/template.j2"), "Original File is deleted")
        self.assertFalse(os.path.isfile("test/many-var/template.j2"), "Original File is deleted")
        os.remove("test/env-var/template")
        os.remove("test/many-var/template")
        subprocess.run("git restore test/*/template.j2", shell = True, executable="/bin/bash")
