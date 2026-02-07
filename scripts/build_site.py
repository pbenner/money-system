from __future__ import annotations

import argparse
from pathlib import Path

from money_system.config import ModelConfig
from money_system.interactive import build_figures, render_figures_html
from money_system.model import MoneySystemModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build GitHub Pages site with interactive plots")
    parser.add_argument("--steps", type=int, default=240, help="Number of monthly steps")
    parser.add_argument("--output-dir", type=Path, default=Path("docs"), help="Output directory")
    return parser.parse_args()


def build_page(figures_html: dict[str, str]) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Money System Simulation</title>
    <script src=\"https://cdn.plot.ly/plotly-2.27.0.min.js\"></script>
    <style>
      :root {{
        --bg: #f5f3ef;
        --ink: #1f1d1a;
        --muted: #5f5a54;
        --accent: #1b4965;
        --card: #ffffff;
      }}
      body {{
        margin: 0;
        font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
        background: var(--bg);
        color: var(--ink);
        line-height: 1.6;
      }}
      header {{
        padding: 48px 24px 24px;
        background: linear-gradient(120deg, #f5f3ef 0%, #e2ddd4 100%);
        border-bottom: 1px solid #ded7ce;
      }}
      header h1 {{
        margin: 0 0 8px 0;
        font-size: 2rem;
        color: var(--accent);
      }}
      header p {{
        margin: 0;
        max-width: 760px;
        color: var(--muted);
      }}
      main {{
        max-width: 1100px;
        margin: 0 auto;
        padding: 24px;
      }}
      section {{
        margin-bottom: 36px;
        background: var(--card);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
      }}
      section h2 {{
        margin-top: 0;
        color: var(--accent);
      }}
      .figure {{
        margin-top: 16px;
      }}
      footer {{
        padding: 24px;
        text-align: center;
        color: var(--muted);
        font-size: 0.9rem;
      }}
      @media (max-width: 720px) {{
        header {{
          padding: 32px 16px 16px;
        }}
        main {{
          padding: 16px;
        }}
      }}
    </style>
  </head>
  <body>
    <header>
      <h1>Money System Simulation</h1>
      <p>
        Stock-flow consistent model with private sector, commercial banks, government, and central bank.
        This page explains the model and embeds the interactive figures alongside the narrative.
      </p>
    </header>
    <main>
      <section>
        <h2>Model Structure</h2>
        <p>
          The model is stock-flow consistent (SFC) and tracks assets, liabilities, and equity for each
          sector: Private, Banks, Government (Treasury), and Central Bank. The core instruments are
          deposits, loans, reserves, government bonds, and the Treasury General Account (TGA).
        </p>
        <p>
          Each transaction is recorded as a set of postings across sector accounts. The bookkeeping
          rule is that the weighted sum of postings equals zero, where assets are positive and
          liabilities and equity are negative. This enforces double-entry accounting across sectors.
        </p>
        <p>
          The term “stock-flow consistent” means that every flow has a matching source and use, every
          stock changes only through recorded flows, and all balance sheets satisfy the same accounting
          identities at every step. This model explicitly enforces those identities.
        </p>
        <pre><code>Transaction balance:  Σ_i s_i · Δx_i = 0
Account sign:          s_i = +1 (asset), -1 (liability/equity)
Balance sheet:         Assets - Liabilities - Equity = 0
Equity residual:       Equity = Assets - Liabilities</code></pre>
        <p>
          The identity Assets − Liabilities − Equity = 0 must hold because equity is defined as the
          residual claim on assets after liabilities are subtracted. If a balance sheet violates this
          identity, the records are inconsistent: either an asset or liability has been misrecorded, or
          equity is not matching the net position. In this model, equity is recomputed each step as
          Assets − Liabilities to guarantee consistency.
        </p>
      </section>

      <section>
        <h2>Money and Debt Dynamics</h2>
        <p>
          Money (M1) is defined as private deposits plus currency. Private debt corresponds to bank loans.
          Loan creation expands both deposits and loans, while repayment contracts them.
        </p>
        <div class=\"figure\">{figures_html["money_debt"]}</div>
      </section>

      <section>
        <h2>Simulation Step (Monthly)</h2>
        <p>Each monthly step follows the same sequence:</p>
        <ol>
          <li>
            Compute interest flows using current balances:
            loan interest, deposit interest, reserve interest, and bond interest.
          </li>
          <li>
            Compute policy flows:
            government spending and taxes (taxes default to a rate on income flows).
          </li>
          <li>
            Compute net loan change:
            positive values create new loans and deposits; negative values repay loans.
          </li>
          <li>
            Apply transactions in order:
            loan creation/repayment, interest flows, government spending, and taxes.
          </li>
          <li>
            Adjust government bond issuance to move the TGA toward its target level.
          </li>
          <li>
            Recompute equity as residual and record a snapshot of all balances and metrics.
          </li>
        </ol>
        <pre><code>Example flow identities (monthly):
Interest on loans    = r_L · Loans
Interest on deposits = r_D · Deposits
Interest on reserves = r_R · Reserves
Interest on bonds    = r_B · GovBonds</code></pre>
        <pre><code>Default behavior rules:
Loan change  = g_L · Loans
Tax base     = G + i_D + i_B - i_L
Taxes        = max(0, τ · Tax base)
Bond issue   = TGA_target - TGA</code></pre>
      </section>

      <section>
        <h2>Bank Reserves</h2>
        <p>
          Reserves are a liability of the central bank and an asset of commercial banks. Fiscal operations
          and interest on reserves shift the reserve balance through the banking system.
        </p>
        <div class=\"figure\">{figures_html["bank_reserves"]}</div>
      </section>

      <section>
        <h2>Bookkeeping Mechanics</h2>
        <p>
          Each flow is implemented as a balanced transaction. For example, government spending
          credits private deposits and bank reserves, while debiting the government TGA and the
          central bank's TGA liability. The transaction is balanced because asset increases are offset
          by liability changes of equal magnitude.
        </p>
        <pre><code>Government spending (amount G):
Private:      Deposits  +G  (asset)
Banks:        Deposits  +G  (liability)
Banks:        Reserves  +G  (asset)
CentralBank:  Reserves  +G  (liability)
CentralBank:  TGA       -G  (liability)
Government:   TGA       -G  (asset)</code></pre>
        <p>
          The model also computes a sectoral identity check to verify that the non-government
          sector's net financial assets equal the negative of the public sector's net position.
        </p>
        <pre><code>NonGov NFA = Private_NFA + Banks_NFA
Public NFP = Government_NFP + CentralBank_NFP
Identity check: NonGov NFA + Public NFP ≈ 0</code></pre>
      </section>

      <section>
        <h2>Fiscal Flows</h2>
        <p>
          Government spending injects deposits into the private sector, while taxes withdraw them.
          The model enforces double-entry bookkeeping for these flows.
        </p>
        <div class=\"figure\">{figures_html["fiscal_flows"]}</div>
      </section>

      <section>
        <h2>Credit Creation and Bond Issuance</h2>
        <p>
          Credit creation is modeled as net loan change. Bond issuance adjusts the Treasury account toward
          its target level, providing the financing counterpart to deficits.
        </p>
        <div class=\"figure\">{figures_html["credit_bonds"]}</div>
      </section>

      <section>
        <h2>Sectoral Net Financial Positions</h2>
        <p>
          In a closed economy with only financial assets, the non-government sector's net financial assets
          are the mirror of the public sector's net position. This relationship should hold each step.
        </p>
        <div class=\"figure\">{figures_html["sectoral_positions"]}</div>
      </section>

      <section>
        <h2>Accounting Check</h2>
        <p>
          The identity check should remain close to zero. Any deviation indicates a bookkeeping imbalance
          or numerical drift.
        </p>
        <div class=\"figure\">{figures_html["accounting_check"]}</div>
      </section>
    </main>
    <footer>
      Generated by money-system simulation.
    </footer>
  </body>
</html>
"""


def main() -> None:
    args = parse_args()
    config = ModelConfig(steps=args.steps)
    model = MoneySystemModel(config)
    results = model.run()

    figures = build_figures(results.stocks, results.flows, results.metrics)
    figures_html = render_figures_html(figures)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "index.html").write_text(build_page(figures_html), encoding="utf-8")

    results.stocks.to_csv(args.output_dir / "stocks.csv", index=False)
    results.flows.to_csv(args.output_dir / "flows.csv", index=False)
    results.metrics.to_csv(args.output_dir / "metrics.csv", index=False)


if __name__ == "__main__":
    main()
