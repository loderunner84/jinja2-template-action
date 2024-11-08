import os
from pathlib import Path
import click
from action.main import Main

@click.command()
#@click.option('--variables', help='Variables', default=None)
@click.option('--keep_template', is_flag=True)
@click.option('--var_file', default=None)
@click.option('--context', multiple=True, default=[])
@click.option('--data_file', default=None)
@click.option('--data_format', default=None)
@click.option('--data_url', default=None)
@click.option('--data_url_format', default=None)
def main(keep_template, var_file, context, data_file, data_format, data_url, data_url_format):
    main = Main(keep_template=keep_template)
    
    if var_file:
        with open(var_file) as f:
            variables = f.read()
        main.addVariables(variables)

    for context_file in context:
        section=Path(os.path.basename(context_file)).stem
        with open(context_file) as f:
            content = f.read()
        if content != "" and content != "null\n":
            main.addJsonSection(section, content)

    if data_file:
        main.addDataFile(data_file, data_format)

    if data_url:
        main.addDataUrl(data_url, data_url_format)
    
    main.renderAll()

if __name__ == '__main__':
    main()