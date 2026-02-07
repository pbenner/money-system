from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class PlotStyle:
    title_size: int = 12
    label_size: int = 10
    grid_alpha: float = 0.25

    def apply(self) -> None:
        plt.rcParams.update(
            {
                "axes.grid": True,
                "grid.alpha": self.grid_alpha,
                "axes.titlesize": self.title_size,
                "axes.labelsize": self.label_size,
                "figure.figsize": (10, 6),
            }
        )


def _select_columns(df: pd.DataFrame, include: Sequence[str] | None) -> List[str]:
    if include is None:
        return list(df.columns)
    out = []
    for name in include:
        if name in df.columns:
            out.append(name)
    return out


def plot_timeseries(
    df: pd.DataFrame,
    series: Sequence[str] | None = None,
    title: str | None = None,
    ylabel: str | None = None,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    cols = _select_columns(df, series)
    if ax is None:
        _, ax = plt.subplots()
    for col in cols:
        ax.plot(df.index, df[col], label=col)
    if title:
        ax.set_title(title)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.set_xlabel("Step")
    if cols:
        ax.legend(loc="best")
    return ax


def plot_sector_balance_sheet(stocks: pd.DataFrame, sector: str) -> plt.Figure:
    cols = [c for c in stocks.columns if c.startswith(f"{sector}:")]
    fig, ax = plt.subplots()
    for col in cols:
        ax.plot(stocks.index, stocks[col], label=col.split(":", 1)[1])
    ax.set_title(f"{sector} Balance Sheet")
    ax.set_xlabel("Step")
    ax.set_ylabel("Level")
    ax.legend(loc="best")
    return fig


def plot_dashboard(
    stocks: pd.DataFrame,
    flows: pd.DataFrame,
    metrics: pd.DataFrame,
    style: PlotStyle | None = None,
) -> plt.Figure:
    if style is None:
        style = PlotStyle()
    style.apply()

    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    plot_timeseries(metrics, ["Money_M1", "Private_Debt"], "Money and Debt", "Level", axes[0, 0])
    plot_timeseries(metrics, ["Bank_Reserves"], "Bank Reserves", "Level", axes[0, 1])
    plot_timeseries(flows, ["gov_spending", "taxes"], "Fiscal Flows", "Flow", axes[1, 0])
    plot_timeseries(flows, ["loan_change", "bond_issuance"], "Credit and Bonds", "Flow", axes[1, 1])
    plot_timeseries(
        metrics,
        ["NonGov_NFA", "Public_NFP"],
        "Sectoral Net Financial Positions",
        "Level",
        axes[2, 0],
    )
    plot_timeseries(
        metrics,
        ["Sector_Balance_Check"],
        "Accounting Check (should be 0)",
        "Level",
        axes[2, 1],
    )
    fig.tight_layout()
    return fig


class LivePlotter:
    def __init__(self, series: Dict[str, List[str]]):
        self.series = series
        self.fig, self.axes = plt.subplots(len(series), 1, figsize=(10, 4 * len(series)))
        if isinstance(self.axes, plt.Axes):
            self.axes = [self.axes]
        else:
            self.axes = list(self.axes)
        self.lines: Dict[str, Dict[str, plt.Line2D]] = {}
        plt.ion()
        self.fig.show()

    def update(self, data: Dict[str, pd.DataFrame]) -> None:
        for ax, (panel, cols) in zip(self.axes, self.series.items()):
            df = data[panel]
            if panel not in self.lines:
                self.lines[panel] = {}
                for col in cols:
                    (line,) = ax.plot(df.index, df[col], label=col)
                    self.lines[panel][col] = line
                ax.set_title(panel)
                ax.legend(loc="best")
            else:
                for col in cols:
                    line = self.lines[panel][col]
                    line.set_data(df.index, df[col])
                ax.relim()
                ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
