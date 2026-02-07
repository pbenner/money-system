from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Sequence

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


@dataclass
class FigureSpec:
    name: str
    title: str
    columns: Sequence[str]
    yaxis_title: str
    dataset: str


def _build_figure(df: pd.DataFrame, columns: Sequence[str], title: str, yaxis: str) -> go.Figure:
    fig = go.Figure()
    for name in columns:
        if name not in df.columns:
            continue
        fig.add_trace(go.Scatter(x=list(df.index), y=df[name], mode="lines", name=name))
    fig.update_layout(title=title, xaxis_title="Step", yaxis_title=yaxis, legend_title_text="Series")
    return fig


def build_figures(
    stocks: pd.DataFrame,
    flows: pd.DataFrame,
    metrics: pd.DataFrame,
) -> Dict[str, go.Figure]:
    specs = [
        FigureSpec(
            name="money_debt",
            title="Money and Private Debt",
            columns=["Money_M1", "Private_Debt"],
            yaxis_title="Level",
            dataset="metrics",
        ),
        FigureSpec(
            name="bank_reserves",
            title="Bank Reserves",
            columns=["Bank_Reserves"],
            yaxis_title="Level",
            dataset="metrics",
        ),
        FigureSpec(
            name="fiscal_flows",
            title="Fiscal Flows",
            columns=["gov_spending", "taxes"],
            yaxis_title="Flow",
            dataset="flows",
        ),
        FigureSpec(
            name="credit_bonds",
            title="Credit Creation and Bond Issuance",
            columns=["loan_change", "bond_issuance"],
            yaxis_title="Flow",
            dataset="flows",
        ),
        FigureSpec(
            name="sectoral_positions",
            title="Sectoral Net Financial Positions",
            columns=["NonGov_NFA", "Public_NFP"],
            yaxis_title="Level",
            dataset="metrics",
        ),
        FigureSpec(
            name="accounting_check",
            title="Accounting Check (should be ~0)",
            columns=["Sector_Balance_Check"],
            yaxis_title="Level",
            dataset="metrics",
        ),
    ]

    datasets = {
        "stocks": stocks,
        "flows": flows,
        "metrics": metrics,
    }

    figures: Dict[str, go.Figure] = {}
    for spec in specs:
        df = datasets[spec.dataset]
        figures[spec.name] = _build_figure(df, spec.columns, spec.title, spec.yaxis_title)
    return figures


def render_figures_html(figures: Dict[str, go.Figure]) -> Dict[str, str]:
    rendered: Dict[str, str] = {}
    for name, fig in figures.items():
        rendered[name] = pio.to_html(fig, include_plotlyjs=False, full_html=False)
    return rendered


def write_dashboard_html(fig: go.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
