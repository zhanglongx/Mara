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

## Known Issues

- `--single` currently converts cumulative quarterly data after applying the date filter. When `start-date` begins mid-year, the first in-range `Q2`/`Q3`/`Q4` row may be reported as a full cumulative value instead of a single-quarter value.
- Multi-indicator merges currently use a left merge based on the longest result set. If different indicators cover different reporting periods, rows that exist only in other indicators can be dropped.
- Multi-indicator output may contain duplicated metadata columns such as `ann_date_x`, `ann_date_y`, `end_date_x`, and `end_date_y`.
- `--sort-by` currently does not take effect for single-indicator `--latest` output, even when the result contains one latest row per stock.
- Stock keyword filtering currently uses regex matching through `pandas.Series.str.contains()`. Literal inputs such as `000001.SZ` or names containing regex metacharacters may match incorrectly or raise errors.

## About

Maragogipe is a variety of Arabica coffee☕. 
