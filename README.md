Sublate is tool for building template based projects with jinja. It can be used for blogs, scaffolds, [themes](https://github.com/subtheme-dev), or any kind of project that renders structured data. 

To install:

    $ pip install sublate

## Quickstart

Sublate works copying project files to an output directory and rendering the selected template files with the supplied data, as configured by a sublate file.

Start by creating `sublate.yaml` at the root of your project, with the location to your data and template files. For example, this project will render `index.html` with the data supplied from `data.json`:

```yaml
# path to data file(s)
# data will not be copied to the output directory
data: "/data.yaml"

# path to template file(s) that will be rendered
render: "/index.html"
```

To build, just run `sublate` from the project directory. This will create an `output` directory with all project files, including the rendered `index.html`.

    $ sublate

## Data Inheritance

Sublate will pass project data to each sub-directory, and data can also be configured from a sub-directory (with another sublate file). Any data configured from a child directory cannot be shared with its parent or sibling directory. All data from the parent is merged with the child, and the child will overwrite any conflicts.
