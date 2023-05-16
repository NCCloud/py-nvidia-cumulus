# Release Process
This document describes how to create a new release

## Steps
Once you are ready to make a new release, perform the following steps:
1. Bump project version in the `pyproject.toml` file.
2. Open a pull requests and assign the `release` label to it.
3. Merge the PR. This will trigger the pipeline which will build and publish the package to PyPI.
4. Create a new release with a description. The release name should include the version from the `pyproject.toml` file.
