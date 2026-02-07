from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from .config import ModelConfig
from .flows import (
    select_transactions,
    tx_bond_issue,
    tx_government_spending,
    tx_interest_on_bonds,
    tx_interest_on_deposits,
    tx_interest_on_loans,
    tx_interest_on_reserves,
    tx_loan_creation,
    tx_loan_repayment,
    tx_private_loan_creation,
    tx_private_loan_repayment,
    tx_taxes,
)
from .ledger import Ledger, build_default_ledger


@dataclass
class SimulationResults:
    stocks: pd.DataFrame
    flows: pd.DataFrame
    metrics: pd.DataFrame


def _get_balance(snapshot: Dict[str, float], sector: str, account: str) -> float:
    return snapshot.get(f"{sector}:{account}", 0.0)


def _compute_metrics(snapshot: Dict[str, float], ledger: Ledger) -> Dict[str, float]:
    deposits = _get_balance(snapshot, "Private", "Deposits")
    currency = _get_balance(snapshot, "Private", "Currency")
    loans = _get_balance(snapshot, "Private", "Loans")
    bonds = _get_balance(snapshot, "Private", "GovBonds")
    reserves = _get_balance(snapshot, "Banks", "Reserves")
    private_nfa = ledger.sectors["Private"].net_position()
    banks_nfa = ledger.sectors["Banks"].net_position()
    public_nfp = ledger.sectors["Government"].net_position() + ledger.sectors["CentralBank"].net_position()
    non_gov_nfa = private_nfa + banks_nfa
    return {
        "Money_M1": deposits + currency,
        "Private_Debt": loans,
        "Private_Bonds": bonds,
        "Bank_Reserves": reserves,
        "Private_NFA": private_nfa,
        "Banks_NFA": banks_nfa,
        "NonGov_NFA": non_gov_nfa,
        "Public_NFP": public_nfp,
        "Sector_Balance_Check": non_gov_nfa + public_nfp,
    }


class MoneySystemModel:
    def __init__(self, config: ModelConfig):
        self.config = config
        initial = config.resolve_initial()
        self.ledger: Ledger = build_default_ledger(initial)
        self._stock_history: List[Dict[str, float]] = []
        self._flow_history: List[Dict[str, float]] = []
        self._metric_history: List[Dict[str, float]] = []

    def snapshot(self) -> Dict[str, float]:
        return self.ledger.snapshot()

    def _resolve_gov_spending(self, step: int) -> float:
        if self.config.gov_spending_fn is not None:
            return float(self.config.gov_spending_fn(step))
        return float(self.config.gov_spending)

    def _resolve_tax(self, step: int, balances: Dict[str, float], flows: Dict[str, float]) -> float:
        if self.config.tax_fn is not None:
            return float(self.config.tax_fn(step, balances))
        tax_base = flows["gov_spending"] + flows["interest_on_deposits"] + flows["interest_on_bonds"]
        tax_base -= flows["interest_on_loans"]
        return max(0.0, self.config.tax_rate * tax_base)

    def _resolve_loan_change(self, step: int, balances: Dict[str, float]) -> float:
        if self.config.loan_growth_fn is not None:
            return float(self.config.loan_growth_fn(step, balances))
        loans = _get_balance(balances, "Private", "Loans")
        return self.config.loan_growth * loans

    def _resolve_private_loan_change(self, step: int, balances: Dict[str, float]) -> float:
        if self.config.private_loan_growth_fn is not None:
            return float(self.config.private_loan_growth_fn(step, balances))
        loans = _get_balance(balances, "Private", "PrivateLoansAsset")
        return self.config.private_loan_growth * loans

    def step(self, step: int) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
        balances = self.snapshot()

        loans = _get_balance(balances, "Private", "Loans")
        deposits = _get_balance(balances, "Private", "Deposits")
        private_loans = _get_balance(balances, "Private", "PrivateLoansAsset")
        bonds = _get_balance(balances, "Private", "GovBonds")
        reserves = _get_balance(balances, "Banks", "Reserves")

        flows = {
            "gov_spending": self._resolve_gov_spending(step),
            "loan_change": self._resolve_loan_change(step, balances),
            "interest_on_loans": self.config.loan_rate * loans,
            "interest_on_deposits": self.config.deposit_rate * deposits,
            "interest_on_reserves": self.config.reserve_rate * reserves,
            "interest_on_bonds": self.config.bond_rate * bonds,
        }
        flows["private_loan_change"] = self._resolve_private_loan_change(step, balances)
        flows["taxes"] = self._resolve_tax(step, balances, flows)

        txs = []
        if flows["loan_change"] >= 0:
            txs.append(tx_loan_creation(flows["loan_change"]))
        else:
            repayment = min(-flows["loan_change"], deposits)
            txs.append(tx_loan_repayment(repayment))

        if flows["private_loan_change"] >= 0:
            txs.append(tx_private_loan_creation(flows["private_loan_change"]))
        else:
            repayment = min(-flows["private_loan_change"], private_loans)
            txs.append(tx_private_loan_repayment(repayment))

        txs.extend(
            [
                tx_interest_on_loans(flows["interest_on_loans"]),
                tx_interest_on_deposits(flows["interest_on_deposits"]),
                tx_interest_on_reserves(flows["interest_on_reserves"]),
                tx_interest_on_bonds(flows["interest_on_bonds"]),
                tx_government_spending(flows["gov_spending"]),
                tx_taxes(flows["taxes"]),
            ]
        )

        for tx in select_transactions(txs):
            self.ledger.apply(tx)

        tga_balance = _get_balance(self.snapshot(), "Government", "TGA")
        tga_gap = self.config.tga_target - tga_balance
        if abs(tga_gap) > 1e-6:
            self.ledger.apply(tx_bond_issue(tga_gap))
            flows["bond_issuance"] = tga_gap
        else:
            flows["bond_issuance"] = 0.0

        equity_adjustments = self.ledger.recompute_equity()

        stocks = self.snapshot()
        metrics = _compute_metrics(stocks, self.ledger)
        for sector, delta in equity_adjustments.items():
            flows[f"equity_adjustment_{sector}"] = delta

        self._stock_history.append(stocks)
        self._flow_history.append(flows)
        self._metric_history.append(metrics)

        return stocks, flows, metrics

    def run(self) -> SimulationResults:
        for step in range(self.config.steps):
            self.step(step)
        stocks = pd.DataFrame(self._stock_history)
        flows = pd.DataFrame(self._flow_history)
        metrics = pd.DataFrame(self._metric_history)
        return SimulationResults(stocks=stocks, flows=flows, metrics=metrics)
