# trivoting

Python library for trichotomous voting.

## Documentation

The complete documentation is available [here](https://comsoc-community.github.io/trivoting/).
It includes
* [installation instructions](https://comsoc-community.github.io/trivoting/installation.html),
* a [short guide](https://comsoc-community.github.io/trivoting/quickstart.html) for a quick start,
* a [complete guide](https://comsoc-community.github.io/trivoting/usage.html) to go further,
* a [reference guide](https://comsoc-community.github.io/trivoting/reference/index.html) to get all the details.

## Development

We are more than happy to receive help with the development of the package.
If you want to contribute, here are some elements to take into account.

First, install the development dependencies by running the following command:
```shell
pip install -e ".[dev]"
```

You can run the unit tests with the following:
```shell
python -m unittest
```

The doc is generated using sphinx. We use the [numpy style guide](https://numpydoc.readthedocs.io/en/latest/format.html).
The [napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) extension for Sphinx is used
and the HTML style is defined by the [Book Sphinx Theme](https://sphinx-book-theme.readthedocs.io/en/stable/).

To generate the doc, first move inside the `docs-source` folder and run the following:
```shell
make clean 
make html
```

This will generate the documentation locally (in the folder `docs-source/build`). If you want the documentation 
to also be updated when pushing, run:
```shell
make githubclean
make github
```

After having pushed, the documentation will be automatically deployed to the GitHub page.

Note that a large part of the documentation is done by hand (to ensure proper display and correct ordering). 
This means that if you create new class of functions that should appear in the documentation, you may have
to add they yourself using to autodoc directives (take inspiration from the files in `docs-source/source`). 

## GitHub Workflow

### Publishing on PyPI

The pipeline between GitHub and PyPI is automatised. To push a new version do the following:
- Update the `pyproject.toml` with the new version number.
- Update the `trivoting/__init__.py` with the new version number.
- On GitHub, create a new release tagged with the new version number (only admins can do that), on [this page](https://github.com/COMSOC-Community/trivoting/releases/new).
- You're done, the new version of the package is automatically pushed to PyPI after the creation of a GitHub release.

### Building the Docs

If the docs-source has been updated but the `docs/` folder has not, you can build the docs via
a GitHub action here: https://github.com/COMSOC-Community/trivoting/actions/workflows/docs.yml.
Simply click "Run workflow" and the docs will be built and the built files will be pushed back to
the server.
