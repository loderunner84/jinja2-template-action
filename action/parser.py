import os
import json
import yaml
import urllib.request
import configparser
from pathlib import Path
from abc import ABC, abstractmethod


class Parser(ABC):

    def __init__(self, format=None):
        if format and format not in self.FORMATS.keys():
            raise ValueError(f"specified format is unknown. Supported format are: {self.FORMATS.keys()}")
        self.format = format

    @abstractmethod
    def load(self):
        pass

    def parse(self):
        self.content = self.load()
        if self.format and self.format not in self.FORMATS.keys():
            raise ValueError(f"specified format is unknown. Supported format are: {self.FORMATS.keys()}")
        
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
            return ('ini',FileParser._parse_ini(content))
        except configparser.Error:
            pass
        try:
            return ('json',FileParser._parse_json(content))
        except json.JSONDecodeError:
            pass
        try:
            return ('env',FileParser._parse_env(content))
        except ValueError:
            pass
        try:
            return ('yaml',FileParser._parse_yaml(content))
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

class UrlParser(Parser):
    def __init__(self, url, waited_format=None):
        self.url = url
        super().__init__(waited_format)
    
    def load(self):
        with urllib.request.urlopen(self.url) as remote_content:
            self.content = remote_content.read()
            content_type = remote_content.getheader('content-type')
            if (self.format == None) and (content_type in UrlParser.CONTENT_TYPE.keys()):
                self.format = UrlParser.CONTENT_TYPE[content_type]
            return self.content

    CONTENT_TYPE = {
        'application/json': 'json',
        'text/json': 'json',
        'application/yaml': 'yaml',
        'application/x-yaml': 'yaml',
        'text/x-yaml': 'yaml',
        'text/yaml': 'yaml'
    }    
            

class FileParser(Parser):

    def __init__(self, file_path, file_format=None):       
        self.file_path = file_path
        super().__init__(file_format)

    def load(self):
        with open(self.file_path, "r") as f:
            self.content = f.read()
        if not self.format:
            self.format = self._getFormatFromExtension(self.file_path)
        return self.content

    @staticmethod
    def _getFormatFromExtension(file_path):
        path = Path(file_path)
        extension = path.suffix.lower().lstrip(".")
        if extension in FileParser.FORMATS.keys():
            return extension
        return None

