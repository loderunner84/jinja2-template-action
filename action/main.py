"""Main file of the jinja2-template-action action."""

import importlib
import base64
import json
import os

from jinja2 import Environment, FileSystemLoader

from .parser import FileParser, UrlParser


class Main:
    """Main class of the jinja2-template-action"""

    def __init__(
        self,
        extensions=(".j2"),
        basepath="./",
        keep_template=False,
        undefined="Undefined",
    ):
        self.ext = extensions
        self.basepath = basepath
        self.keep_template = keep_template
        if undefined not in self.BEHAVIOURS:
            raise ValueError(f"Specified Undefined Behavior is unknow: {undefined}")
        undefined_class = Main.class_for_name("jinja2", undefined)
        self.env = Environment(
            loader=FileSystemLoader(self.basepath), undefined=undefined_class
        )
        # Add some custom filters
        self.env.filters['b64encode'] = lambda s: base64.b64encode(s.encode("ascii"))
        self.data = {}
        # Keep the environ method in template as whe have in the
        # jinja2 cli in the first version of this action
        self.env.globals["environ"] = os.environ.get
        # Also add env variable in a classic way env.VAR_NAME
        self.data["env"] = dict(os.environ)

    BEHAVIOURS = [
        "Undefined",
        "ChainableUndefined",
        "DebugUndefined",
        "StrictUndefined",
    ]

    @staticmethod
    def class_for_name(module_name, class_name):
        """Load Class"""
        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        c = getattr(m, class_name)
        return c

    def add_variables(self, variables):
        """
        Add Variables in the jinja2 context
          Parameters:
          variables (str): Envrionement Variable list, one declaration by line
            with a = between the key and the value
        """
        for variable in variables.split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                self.data.update({name: value})

    def add_json_section(self, section_name, json_content):
        """
        Add Json Data in a given section to the Data available to the template engine
          Parameters:
            sectionName (str): Name of the added section. The jsconContent will be encapsuled
              in this key.
            jsonContent (str/dict): Json content added in the key defined by sectionName
        """
        if isinstance(json_content, str):
            data = json.loads(json_content)
        elif isinstance(json_content, dict):
            data = json_content
        else:
            raise ValueError(f"Unknown type for jsonContent: {type(json_content)}")

        # protect again key contening dashes (it is the case in the keys of strategy
        # context for example)
        problematic_keys = [key for key in data.keys() if "-" in key]
        for problematic_key in problematic_keys:
            new_key = problematic_key.replace("-", "_")
            data[new_key] = data.pop(problematic_key)
        self.data[section_name] = data

    def add_data_file(self, file_path, file_format=None):
        """
        Add Variable from a file to jinja2 context.
        """
        parser = FileParser(file_path, file_format)
        content = parser.parse()
        self.data.update(content)

    def add_data_url(self, url, data_format=None):
        """
        Add Variable from a url to jinja2 context.
        """
        parser = UrlParser(url, data_format)
        content = parser.parse()
        self.data.update(content)

    def render_file(self, file_path):
        """
        Render One File with saved jinja2 context.
        """
        with open(f"{file_path}".rsplit(".", 1)[0], "w", encoding="utf-8") as out:
            out.write(self.env.get_template(f"{file_path}").render(self.data))
            out.flush()
        if not self.keep_template:
            os.remove(f"{file_path}")

    def render_all(self):
        """
        Render All File with saved jinja2 context.
        """
        for path, _, files in os.walk(self.basepath):
            for name in files:
                if name.endswith(self.ext):
                    self.render_file(f"{path}/{name}")
