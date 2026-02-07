# Money System Simulation

This project provides a stock-flow consistent (SFC) simulation of a money system with the private sector, commercial banks, government (treasury), and central bank. It maintains full bookkeeping with explicit assets, liabilities, and equity for each sector.

## Quick start

1. Create a virtual environment and install dependencies.
2. Run the example simulation script:

```bash
python -m scripts.run_sim
```

The script will run a monthly simulation, save CSV outputs, and generate plots.

## Structure

- `src/money_system/ledger.py` double-entry ledger and balance sheet validation
- `src/money_system/flows.py` reusable transaction builders
- `src/money_system/model.py` core simulation model and behavior rules
- `src/money_system/plotting.py` plotting utilities (static and live)
- `src/money_system/interactive.py` interactive Plotly dashboard
- `scripts/run_sim.py` example runner
- `scripts/build_site.py` generate `docs/index.html` for GitHub Pages

## Extending

- Add accounts or sectors in `default_chart()`.
- Add new transactions in `flows.py`.
- Override behavior rules in `ModelConfig` or by subclassing the model.

## GitHub Pages

Build the interactive dashboard into `docs/index.html`:

```bash
python -m scripts.build_site
```

Then enable GitHub Pages in the repo settings with:
- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

The generated site includes a short model explanation with each figure embedded in the text.
