import os
import json
from jinja2 import Template, Environment, FileSystemLoader
from .parser import FileParser

class Main:
    def __init__(self, extensions=('.j2'), basepath='./', keep_template=False):
        self.ext = extensions
        self.basepath = basepath
        self.keep_template = keep_template
        self.env = Environment(
            loader=FileSystemLoader(self.basepath)
        )
        self.data = {}
        # Keep the environ method in template as whe have in the 
        #jinja2 cli in the first version of this action
        self.env.globals["environ"] = lambda key: os.environ.get(key)
        # Also add env variable in a classic way env.VAR_NAME
        self.data["env"] = dict(os.environ)

    def addVariables(self, variables):
        for variable in variables.split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                self.data.update({name: value})

    def addJsonSection(self, sectionName, jsonContent):
        '''
        Add Json Data in a given section to the Data available to the template engine
          Parameters:
            sectionName (str): Name of the added section. The jsconContent will be encapsuled in this key.
            jsonContent (str/dict): Json content added in the key defined by sectionName
        '''
        if isinstance(jsonContent, str):
            data = json.loads(jsonContent)
        elif isinstance(jsonContent, dict):
            data = jsonContent
        else:
            raise Exception(f"Unknown type for jsonContent: {type(jsonContent)}")
        
        # protect again key contening dashes (it is the case in the keys of strategy context for example)
        problematic_keys = [key for key in data.keys() if '-' in key] 
        for problematic_key in problematic_keys:
            new_key = problematic_key.replace("-", "_")
            data[new_key] = data.pop(problematic_key)
        
        self.data[sectionName] = data

    def addDataFile(self, file_path, file_format=None):
        parser = FileParser(file_path, file_format)
        content = parser.parse()
        self.data.update(content)

    def addDataUrl(self, url, data_format=None): 
        pass
    
    def renderFile(self, filePath):
        with open(f"{filePath}".rsplit(".", 1)[0], 'w') as out:
            out.write(self.env.get_template( f"{filePath}").render(self.data))
            out.flush()
        if not self.keep_template:
            os.remove(f"{filePath}")

    def renderAll(self):
        for path, dirc, files in os.walk(self.basepath):
            for name in files:
                if name.endswith(self.ext):
                    self.renderFile(f"{path}/{name}")


