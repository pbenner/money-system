from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


@dataclass
class InteractivePanel:
    title: str
    columns: Sequence[str]
    yaxis_title: str


@dataclass
class InteractiveLayout:
    title: str = "Money System Dashboard"
    height: int = 900


def _add_series(fig: go.Figure, df: pd.DataFrame, cols: Sequence[str], row: int, col: int) -> None:
    for name in cols:
        if name not in df.columns:
            continue
        fig.add_trace(
            go.Scatter(x=list(df.index), y=df[name], mode="lines", name=name),
            row=row,
            col=col,
        )


def build_dashboard(
    stocks: pd.DataFrame,
    flows: pd.DataFrame,
    metrics: pd.DataFrame,
    layout: InteractiveLayout | None = None,
) -> go.Figure:
    if layout is None:
        layout = InteractiveLayout()

    panels: List[InteractivePanel] = [
        InteractivePanel("Money and Debt", ["Money_M1", "Private_Debt"], "Level"),
        InteractivePanel("Bank Reserves", ["Bank_Reserves"], "Level"),
        InteractivePanel("Fiscal Flows", ["gov_spending", "taxes"], "Flow"),
        InteractivePanel("Credit and Bonds", ["loan_change", "bond_issuance"], "Flow"),
        InteractivePanel("Sectoral Net Positions", ["NonGov_NFA", "Public_NFP"], "Level"),
        InteractivePanel("Accounting Check", ["Sector_Balance_Check"], "Level"),
    ]

    fig = make_subplots(rows=3, cols=2, subplot_titles=[p.title for p in panels])
    datasets = [metrics, metrics, flows, flows, metrics, metrics]

    for idx, panel in enumerate(panels):
        row = idx // 2 + 1
        col = idx % 2 + 1
        df = datasets[idx]
        _add_series(fig, df, panel.columns, row, col)

    fig.update_layout(title=layout.title, height=layout.height, legend_title_text="Series")
    fig.update_xaxes(title_text="Step")
    return fig


def write_dashboard_html(fig: go.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
