import os
from jinja2 import Template, Environment, FileSystemLoader

class Main:
    def __init__(self, extensions=('.j2'), basepath='./'):
        self.ext = extensions
        self.basepath = basepath
        self.env = Environment(
            loader=FileSystemLoader(self.basepath)
        )
        self.data = {}
        # Keep the environ method in template as whe have in the 
        #jinja2 cli in the first version of this action
        self.env.globals["environ"] = lambda key: os.environ.get(key)

    def addVariables(self, variables):
        for variable in variables.split("\n"):
            clean_variable = bytes(variable.strip(), "utf-8").decode("unicode_escape")
            if clean_variable != "":
                name, value = clean_variable.split("=", 1)
                self.data.update({name: value})
    
    def renderFile(self, filePath):
        with open(f"{filePath}".rsplit(".", 1)[0], 'w') as out:
            out.write(self.env.get_template( f"{filePath}").render(self.data))
            out.flush()
        os.remove(f"{filePath}")

    def renderAll(self):
        for path, dirc, files in os.walk(self.basepath):
            for name in files:
                if name.endswith(self.ext):
                    self.renderFile(f"{path}/{name}")



