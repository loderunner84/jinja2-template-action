# jinja2-template-action

Use Jinja2 template engine on multipe files as a GitHub Action.

[![Continuous Testing](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml/badge.svg)](https://github.com/fletort/jinja2-template-action/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/fletort/jinja2-template-action/badge.svg?branch=main)](https://coveralls.io/github/fletort/jinja2-template-action?branch=main)
[![Testspace tests count](https://img.shields.io/testspace/total/fletort/fletort%3Ajinja2-template-action/main)](https://fletort.testspace.com/projects/68162/spaces)

## Behaviour

This action transfrom all local j2 files (recursively) ('\*.j2')
with the jinja2 library.

- All the detect template will be resolve and named without the j2 extension.
  For exemple, `README.md.j2` becomes `README.md`.
- Original template file can be keep or not (not keeped by default)
- All gihub contextes are available inside template (`github`, `job`,
  `runner`, `strategy`, `matrix`)
- It is possible to give more input variables to the jinja2 engine in
  multiple way:
  - From environement variables,
  - From variable given in input,
  - From local data files in multipe possible format (`env`, `yaml`, `json`, `ini`)
  - From URL source in multipe possible format (`env`, `yaml`, `json`, `ini`)
- The behaviour of the jinje2 engine on not defined value can be defined

## Usage

### Using Environment Variable

```yaml
- uses: fletort/jinja2-template-action@v1
  env:
    TEST: my_value
```

Environment variables are used as with jinja2 cli:

```file
{{ environ('TEST') }}
```

Or as other contextual GitHub information:

```file
{{ env.TEST }}
```

### Using Input Variables

```yaml
- uses: fletort/jinja2-template-action@v1
  with:
    variables: |
      TEST1=mytest
      TEST2=isfunny
```

### Using Data Files

```yaml
- uses: fletort/jinja2-template-action@v1
  with:
    data_file: my_data.json
    data_format: json # can be detected automatically (see below)
```

Possible data type are: `env`, `yaml`, `json`, `ini`

#### 1. env file

```file
EXEMPLE_SMART=yoyo
EXEMPLE_MY_VAR=True
```

#### 2. ini

```file
[EXEMPLE]
SMART=yoyo
MY_VAR=True
```

#### 3. YAML

```file
---
EXEMPLE:
  SMART=yoyo
  MY_VAR=True
```

#### 4. json

```file
{
  "EXEMPLE": {
    "SMART": "yoyo",
    "MY_VAR": True
  }
}
```

#### Related Jinja Template

For previous INI, YAML, JSON examples, jinja template will be:

```file
{{ EXEMPLE.SMART }}
{{ EXEMPLE.MY_VAR }}
```

For previous ENV example, jinja template will be:

```file
{{ EXEMPLE_SMART }}
{{ EXEMPLE_MY_VAR }}
```

### Using URL data source

URL can also be used as data source, in the same previous format.
The exemple below see the use of a data file from another repository.

```yaml
- uses: fletort/jinja2-template-action@v1
  with:
    data_url: https://raw.githubusercontent.com/owner/anoter-repo/refs/heads/main/my_var.yml
    data_format: yaml # can be detected automatically (see below)
```

### Using Workflow GitHub contextual Information

Some of the [contextual information about workflow runs](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/accessing-contextual-information-about-workflow-runs)
are available inside your jinja Template:

- `github`
- `job`
- `runner`
- `strategy`
- `matrix`

As part of an expression, you can access context information using one of two syntaxes.
Index syntax: `github['sha']`
Property dereference syntax: `github.sha`

```file
{{ github.repository }}
{{ job.status }}
{{ runner.os }}
{{ strategy.job_index }}
{{ matrix.your_matrix_variable_name }}
```

Note: All strategy information key contains dashes that must me marked as
underscore in jinja expression: `${{ strategy.job-index }}` becomes
`{{ strategy.job_index }}`.

### Actions inputs

<!-- prettier-ignore-start -->
| Name | Description | Default |
| ---- | ----------- | ------- |
| `variables` | Variable to substitute in the jinja templates. Must be Key, value pairs in .env file format (key=value). | "" |
| `keep_template` | Put to `true` to keep original template file. | `false` |
| `data_file` | Source file contening inputs variable for the jinja template. | "" |
| `data_format` | Format of the `data_file`. Can be `env`, `ini`, `yaml`, `json` or `automatic` (for automatic detection). The automatic detection is based on the extension then on the content. | `automatic` |
| `data_url` | URL Link contening inputs variable for the jinja template. | "" |
| `data_url_format` | Format of the `data_url`. Can be `env`, `ini`, `yaml`, `json` or `automatic` (for automatic detection). The automatic detection is based on the http header content-type then on the content itself. | `automatic` |
| `undefined_behaviour` | Define the behaviour when a not defined variable is found. Can be `Undefined`, `ChainableUndefined`, `DebugUndefined` or `StrictUndefined`. [See below for more information.](#undefined-behaviour) | `Undefined` |
<!-- prettier-ignore-end -->

#### Undefined Behaviour

It is possible to define how jinja 2 engine manage undefined value.
Actually only behavior [proposed by Jinja2 library](https://jinja.palletsprojects.com/en/stable/api/#undefined-types)
can be used: `Undefined`, `ChainableUndefined`, `DebugUndefined` or `StrictUndefined`.

When a simple variable is not defined:

- `Undefined` and `ChainableUndefined` return an empty string
- `DebugUndefined` keeps the variable name
- `StrictUndefined` raises en error

When trying to accessing a undefined key of an existing dictionnary:

- `Undefined` and `ChainableUndefined` return an empty string
- `DebugUndefined` write a warning of type
  `{{ no such element: dict object['my_key'] }}`
- `StrictUndefined` raises en error

When trying to accessing a undefined key of an undefined dictionnary:

- `Undefined`, `DebugUndefined` and `StrictUndefined` raises en error
- `ChainableUndefined` return an empty string

For exemple with the following data:

```yaml
defined: value
with_key:
  ok: toto
```

Results are:

| Test / Behavior       | Undefined | ChainableUndefined | DebugUndefined                             | StrictUndefined |
| --------------------- | --------- | ------------------ | ------------------------------------------ | --------------- |
| `{{ defined }}`       | 'value'   | 'value'            | 'value'                                    | 'value'         |
| `{{ not_defined }}`   | ''        | ''                 | '{{ not_defined }}'                        | **ERROR**       |
| `{{ with_key.ok }}`   | 'toto'    | 'toto'             | 'toto'                                     | 'toto'          |
| `{{ with_key.ko }}`   | ''        | ''                 | "{{ no such element: dict object['ko'] }}" | **ERROR**       |
| `{{ not_defined.t }}` | **ERROR** | ''                 | **ERROR**                                  | **ERROR**       |
| `{{ with_key.ok.a }}` | ''        | ''                 | "{{ no such element: str object['a'] }}"   | **ERROR**       |
| `{{ with_key.ko.a }}` | **ERROR** | ''                 | **ERROR**                                  | **ERROR**       |

## Code Quality

All unit test executed on each branch/PR are listed/described on
[testspace](https://fletort.testspace.com/projects/68162/spaces).

Coverage information and history is also avalailable on [coveralls](https://coveralls.io/github/fletort/jinja2-template-action).

## License

The scripts and documentation in this project are released under the
[MIT License](LICENSE)
