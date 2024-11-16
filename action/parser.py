"""
Parser Module
"""

import configparser
import json
import urllib.request
from abc import ABC, abstractmethod
from pathlib import Path

import yaml


class Parser(ABC):
    """Abstract Parser Base Class"""

    def __init__(self, parser_format=None):
        if parser_format and parser_format not in self.FORMATS:
            raise ValueError(
                "specified format is unknown."
                f"Supported format are: {self.FORMATS.keys()}"
            )
        self.format = parser_format
        self.content = ""

    @abstractmethod
    def load(self):
        """Load the content to Parse (must be impletend in child class)"""

    def parse(self):
        """Load and Parse the content"""
        self.content = self.load()
        if self.format and self.format not in self.FORMATS:
            raise ValueError(
                "specified format is unknown."
                f"Supported format are: {self.FORMATS.keys()}"
            )

        if self.format:
            content = getattr(FileParser, self.FORMATS[self.format])(self.content)
        else:
            content = self._parse_generic(self.content)

        return content

    @staticmethod
    def _parse_ini(content):
        config_object = configparser.ConfigParser()
        config_object.optionxform = str
        config_object.read_string(content)
        output_dict = {
            s: dict(config_object.items(s)) for s in config_object.sections()
        }
        return output_dict

    @staticmethod
    def _parse_json(content):
        return json.loads(content)

    @staticmethod
    def _parse_yaml(content):
        return yaml.safe_load(content)

    @staticmethod
    def _parse_env(content):
        output_dict = {}
        for variable in content.split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                output_dict.update({name: value})
        return output_dict

    @staticmethod
    def _parse_generic(content):
        try:
            return ("ini", Parser._parse_ini(content))
        except configparser.Error:
            pass
        try:
            return ("json", Parser._parse_json(content))
        except json.JSONDecodeError:
            pass
        try:
            return ("env", Parser._parse_env(content))
        except ValueError:
            pass
        try:
            return ("yaml", Parser._parse_yaml(content))
        except yaml.YAMLError:
            pass

        raise ValueError("File format is not automatically recognized")

    FORMATS = {
        "ini": "_parse_ini",
        "json": "_parse_json",
        "yml": "_parse_yaml",
        "yaml": "_parse_yaml",
        "env": "_parse_env",
    }


class UrlParser(Parser):
    """Parser dedicated to Url Content"""

    def __init__(self, url, waited_format=None):
        self.url = url
        super().__init__(waited_format)

    def load(self):
        with urllib.request.urlopen(self.url) as remote_content:
            self.content = remote_content.read()
            content_type = remote_content.getheader("content-type")
            if (self.format is None) and (content_type in UrlParser.CONTENT_TYPE):
                self.format = UrlParser.CONTENT_TYPE[content_type]
            return self.content

    CONTENT_TYPE = {
        "application/json": "json",
        "text/json": "json",
        "application/yaml": "yaml",
        "application/x-yaml": "yaml",
        "text/x-yaml": "yaml",
        "text/yaml": "yaml",
    }


class FileParser(Parser):
    """Parser dedicated to File"""

    def __init__(self, file_path, file_format=None):
        self.file_path = file_path
        super().__init__(file_format)

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.content = f.read()
        if not self.format:
            self.format = self._get_format_from_extension(self.file_path)
        return self.content

    @staticmethod
    def _get_format_from_extension(file_path):
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        if extension in FileParser.FORMATS:
            return extension
        return None
