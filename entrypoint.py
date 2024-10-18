import os
import click
from action.main import Main

@click.command()
#@click.option('--variables', help='Variables', default=None)
def main():
    main = Main()
    variables = os.environ.get('INPUT_VARIABLES', '')
    if variables:
        main.addVariables(variables)
    main.renderAll()

if __name__ == '__main__':
    main()