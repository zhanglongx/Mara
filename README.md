# Mara

Mara is a plotting tool that takes data from tushare and plots it through matplotlib.

## Usage

1. Prepare TEMPLATE file:

```yaml
  global:
    # tushare token
    token: 'f4673f7862e73483c5e65cd9a036eedd39e72d484194a85dabcf958b'

  plots:
    # plot name. this field will also be used to lookup
    # columns from tushare, or assigned as left side of formula
  - name: 'fixed_assets'
    # if number of symbols > 1, plot in side-by-side axes
    separate: true
    # any plot() kwargs, will directly passed to plot()
    kind: 'bar'
  - name: 'id_ratio'
    # for advanced use, assign a formula
    formula: 'id_ratio = interestdebt / fixed_assets'
    separate: true
    kind: 'line'
```

NOTE: name and formula only support mandatory columns (with Y) from tushare fina_indicator 

2. run main.py

```bash
	$ python main.py [-h] [-c] [-t TEMPLATE] symbols [symbols ...]
```

## About

Maragogipe is a variety of Arabica coffee☕. 