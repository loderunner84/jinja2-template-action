import os
import json
import yaml
import configparser
from pathlib import Path


class Parser:

    def __init__(self, file_path, file_format=None):
        if file_format and file_format not in self.FORMATS.keys():
            raise ValueError(f"specified format is unknown. Supported format are: {self.FORMATS.keys()}")
        if not file_format:
            file_format = self._getFormatFromExtension(file_path)
        self.file_format = file_format
        self.file_path = file_path

    def parse(self):
        with open(self.file_path, "r") as f:
            file_content = f.read()
        if self.file_format:
            content = getattr(Parser, self.FORMATS[self.file_format])(file_content)
        else:
            content = self._parse_generic(file_content)
        
        return content

    @staticmethod
    def _getFormatFromExtension(file_path):
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        if extension in Parser.FORMATS.keys():
            return extension
        return None
    
    @staticmethod
    def _parse_ini(content):
        config_object = configparser.ConfigParser()
        config_object.optionxform = str
        config_object.read_string(content)
        output_dict={s:dict(config_object.items(s)) for s in config_object.sections()}
        return output_dict
    
    @staticmethod
    def _parse_json( content):
        return json.loads(content)

    @staticmethod
    def _parse_yaml( content):
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
            return ('ini',Parser._parse_ini(content))
        except configparser.Error:
            pass
        try:
            return ('json',Parser._parse_json(content))
        except json.JSONDecodeError:
            pass
        try:
            return ('env',Parser._parse_env(content))
        except ValueError:
            pass
        try:
            return ('yaml',Parser._parse_yaml(content))
        except yaml.YAMLError:
            pass

        raise ValueError(f"File format is not automatically recognized")

    FORMATS = {
        'ini':  '_parse_ini',
        'json': '_parse_json',
        'yml': '_parse_yaml',
        'yaml': '_parse_yaml',
        'env': '_parse_env'
    }