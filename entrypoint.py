"""
CLI Entrypoint
"""

import os
from pathlib import Path

import click

from action.main import Main


@click.command()
@click.option("--keep_template", is_flag=True)
@click.option("--var_file", default=None)
@click.option("--context", multiple=True, default=[])
@click.option("--data_file", default=None)
@click.option("--data_format", default=None)
@click.option("--data_url", default=None)
@click.option("--data_url_format", default=None)
@click.option("--undefined_behaviour", default="Undefined")
def main(  # pylint: disable=R0913
    keep_template,
    var_file,
    context,
    data_file,
    data_format,
    data_url,
    data_url_format,
    undefined_behaviour,
):
    """Main CLI Method"""
    m = Main(keep_template=keep_template, undefined=undefined_behaviour)

    if var_file:
        with open(var_file, encoding="utf-8") as f:
            variables = f.read()
        m.add_variables(variables)

    for context_file in context:
        section = Path(os.path.basename(context_file)).stem
        with open(context_file, encoding="utf-8") as f:
            content = f.read()
        if content not in ("", "null\n"):
            m.add_json_section(section, content)

    if data_file:
        m.add_data_file(data_file, data_format)

    if data_url:
        m.add_data_url(data_url, data_url_format)

    m.render_all()


if __name__ == "__main__":
    main()  # pylint: disable=E1120
