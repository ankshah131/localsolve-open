# General dev setup

This monorepo uses pre-commit hooks to run automated tooling - ensuring code
quality and to prevent syntactically broken code from entering the codebase.
To set up the pre-commit hooks:

- Install pre-commit
  - Projects will likely have pre-commit as a dev dependency anyway, so you may not have to separately install it.
  - Separate installation can be done via [brew](https://formulae.brew.sh/formula/pre-commit), via [conda](https://anaconda.org/conda-forge/pre_commit), or via [pip](https://pypi.org/project/pre-commit/)
- Run `pre-commit install`
  - This will mean that pre-commit runs on every commit that you make

See pre-commmit's usage section for info on manually running the rool. See the
`.pre-commit-config.yaml` file for info on which hooks are configured.

See the `CONTRIBUTING.md` file in project folders for project specific dev setup instructions.
