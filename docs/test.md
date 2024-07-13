# Testing

## Ruff

Ruff is used for linting and testing.

VS Code Extension: <https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff>

Linting is done with Ruff (<https://github.com/astral-sh/ruff>) for all `*.py` files checked in to Git.

```bash
ruff check .    
```

Ruff allows formatting as well.

```bash
ruff format . 
```

## Pytest

To test our code we are writing tests utilizing the official Python recommendation: **pytest**. Each subfolder in `/src` has its own `/test` folder holding the testfiles. We are thriving to keep a coverage of 80% of our `/src` folder.
Shared test functionality, which is used in multiple test files can be found in `src/helper/test_base`.
