# Mara

Mara is an analysis and plotting tool that takes data from tushare and plots it through matplotlib.

## Development Setup

Use Python 3.12+ and the local `.venv` environment.

```bash
./.venv/bin/pip install -e ".[dev]"
```

## Usage

1. Prepare the `~/.mararc` file (YAML syntax):

```yaml
token: "<tushare token>"
```
2. Install the package in your environment:

```bash
./.venv/bin/pip install -e .
```
3. Run the CLI:

```bash
mara [OPTIONS] [KEYWORD [KEYWORD ...]]
```

Example:

```bash
mara -i roe,debt_to_assets -s 2020-01-01 -e 2023-01-01 000001.SZ 600000.SH
```

## About

Maragogipe is a variety of Arabica coffee☕. 
