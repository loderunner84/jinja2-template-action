import os
from pathlib import Path
import click
from action.main import Main

@click.command()
#@click.option('--variables', help='Variables', default=None)
@click.option('--keep_template', is_flag=True)
@click.option('--var_file', default=None)
@click.option('--context', multiple=True, default=[])
def main(keep_template, var_file, context):
    main = Main(keep_template=keep_template)
    
    if var_file:
        with open(var_file) as f:
            variables = f.read()
        main.addVariables(variables)

    for context_file in context:
        section=Path(os.path.basename(context_file)).stem
        with open(context_file) as f:
            content = f.read()
        main.addJsonSection(section, content)
    
    main.renderAll()

if __name__ == '__main__':
    main()