# jinja2-template-action
Use Jinja2 template engine on multipe files as a GitHub action.

[![Continuous Testing](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml/badge.svg)](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml)

This is a very simple version of the action, that is ok for my first need.
Futur enhancement will come.

The actual "simple" version transform all local j2 files (recursively) ('*.j2')
with the jinja2 cli.

The new file name is the same filename without the j2 extension.
For exemple, `README.md.j2` becomes `README.md`.

It this version, it can only be used with environment variable, see my [test template file](./test/template.j2).

## Usage

<!-- start usage -->

```yaml
- uses: fletort/jinja2-template-action@v1
```
<!-- end usage -->

## Future Enhancement

- Insert all github context
- Insert Variable files in input (in various format)
- Error Mode: can exit in error in variable are missing to fill all the template
- ...

## Code Quality

All unit test executed on each branch/PR are listed/described on
[testspace](https://fletort.testspace.com/projects/68162/spaces).

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE)
