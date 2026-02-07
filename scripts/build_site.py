from __future__ import annotations

import argparse
from pathlib import Path

from money_system.config import ModelConfig
from money_system.interactive import InteractiveLayout, build_dashboard, write_dashboard_html
from money_system.model import MoneySystemModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build GitHub Pages site with interactive plots")
    parser.add_argument("--steps", type=int, default=240, help="Number of monthly steps")
    parser.add_argument("--output-dir", type=Path, default=Path("docs"), help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ModelConfig(steps=args.steps)
    model = MoneySystemModel(config)
    results = model.run()

    layout = InteractiveLayout(title="Money System Simulation")
    fig = build_dashboard(results.stocks, results.flows, results.metrics, layout=layout)
    write_dashboard_html(fig, args.output_dir / "index.html")

    results.stocks.to_csv(args.output_dir / "stocks.csv", index=False)
    results.flows.to_csv(args.output_dir / "flows.csv", index=False)
    results.metrics.to_csv(args.output_dir / "metrics.csv", index=False)


if __name__ == "__main__":
    main()
