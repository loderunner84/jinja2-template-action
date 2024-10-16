# jinja2-template-action
Use Jinja2 template engine on multipe files as a GitHub action.

[![Continuous Testing](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml/badge.svg)](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/fletort/jinja2-template-action/badge.svg?branch=main)](https://coveralls.io/github/fletort/jinja2-template-action?branch=main)
[![Testspace tests count](https://img.shields.io/testspace/total/fletort/fletort%3Ajinja2-template-action/main)](https://fletort.testspace.com/spaces/68162/current)

This is a very simple version of the action, that is ok for my first need.
Futur enhancement will come.

The actual "simple" version transform all local j2 files (recursively) ('*.j2')
with the jinja2 library.

The new file name is the same filename without the j2 extension.
For exemple, `README.md.j2` becomes `README.md`.

It this version, it can only be used with environment variable, see my [test template file](./test/template.j2).

Environement variable as used as with the jinja2 cli, with a _kind_ of `environ` method :
```
{{ environ('TEST') }}
```

## Usage

<!-- start usage -->

```yaml
- uses: fletort/jinja2-template-action@v1
```
<!-- end usage -->

## Code Quality

All unit test executed on each branch/PR are listed/described on
[testspace](https://fletort.testspace.com/projects/68162/spaces).

Coverage information and history is also avalailable on [coveralls](https://coveralls.io/github/fletort/jinja2-template-action).

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE)
