from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from money_system.config import ModelConfig
from money_system.model import MoneySystemModel
from money_system.plotting import LivePlotter, PlotStyle, plot_dashboard, plot_sector_balance_sheet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run money system simulation")
    parser.add_argument("--steps", type=int, default=120, help="Number of monthly steps")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output directory")
    parser.add_argument("--no-plots", action="store_true", help="Disable plotting")
    parser.add_argument("--live", action="store_true", help="Enable live plotting")
    return parser.parse_args()


def run_static(model: MoneySystemModel, output_dir: Path) -> None:
    results = model.run()
    output_dir.mkdir(parents=True, exist_ok=True)
    results.stocks.to_csv(output_dir / "stocks.csv", index=False)
    results.flows.to_csv(output_dir / "flows.csv", index=False)
    results.metrics.to_csv(output_dir / "metrics.csv", index=False)

    style = PlotStyle()
    fig = plot_dashboard(results.stocks, results.flows, results.metrics, style=style)
    fig.savefig(output_dir / "dashboard.png", dpi=150)

    for sector in ["Private", "Banks", "Government", "CentralBank"]:
        fig = plot_sector_balance_sheet(results.stocks, sector)
        fig.savefig(output_dir / f"balance_sheet_{sector.lower()}.png", dpi=150)


def run_live(model: MoneySystemModel, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plotter = LivePlotter(
        {
            "metrics": ["Money_M1", "Private_Debt", "Bank_Reserves", "NonGov_NFA", "Public_NFP"],
            "flows": ["gov_spending", "taxes", "loan_change", "bond_issuance"],
        }
    )

    for step in range(model.config.steps):
        model.step(step)
        plotter.update(
            {
                "metrics": _to_frame(model._metric_history),
                "flows": _to_frame(model._flow_history),
            }
        )

    # Save outputs after the live run
    results = model.run() if not model._stock_history else None
    if results is None:
        stocks_df = _to_frame(model._stock_history)
        flows_df = _to_frame(model._flow_history)
        metrics_df = _to_frame(model._metric_history)
    else:
        stocks_df = results.stocks
        flows_df = results.flows
        metrics_df = results.metrics

    stocks_df.to_csv(output_dir / "stocks.csv", index=False)
    flows_df.to_csv(output_dir / "flows.csv", index=False)
    metrics_df.to_csv(output_dir / "metrics.csv", index=False)

    plt.ioff()
    plt.show()


def _to_frame(history):
    import pandas as pd

    return pd.DataFrame(history)


def main() -> None:
    args = parse_args()
    config = ModelConfig(steps=args.steps)
    model = MoneySystemModel(config)

    if args.no_plots:
        results = model.run()
        args.output_dir.mkdir(parents=True, exist_ok=True)
        results.stocks.to_csv(args.output_dir / "stocks.csv", index=False)
        results.flows.to_csv(args.output_dir / "flows.csv", index=False)
        results.metrics.to_csv(args.output_dir / "metrics.csv", index=False)
        return

    if args.live:
        run_live(model, args.output_dir)
    else:
        run_static(model, args.output_dir)


if __name__ == "__main__":
    main()
