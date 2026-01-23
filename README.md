# Mara

Mara is an analysis and plotting tool that takes data from tushare and plots it through matplotlib.

## Usage

1. Prepare the ~/.mararc file(yaml syntax):

```yaml
  token: '<tushare token>'
```
2. run mara.py

```bash
	$ python3 mara.py [OPTIONS] [KEYWORD [KEYWORD ...]]
```
Example:

```bash
	$ python3 mara.py -i roe,debt_to_assets -s 2020-01-01 -e 2023-01-01 000001.SZ 600000.SH
```

## About

Maragogipe is a variety of Arabica coffee☕. 