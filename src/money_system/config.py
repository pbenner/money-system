from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict


@dataclass
class ModelConfig:
    steps: int = 120
    dt_months: float = 1.0

    # Policy and behavioral parameters (monthly rates by default)
    gov_spending: float = 100.0
    tax_rate: float = 0.2
    loan_growth: float = 0.01
    private_loan_growth: float = 0.0

    deposit_rate: float = 0.01 / 12.0
    loan_rate: float = 0.04 / 12.0
    reserve_rate: float = 0.02 / 12.0
    bond_rate: float = 0.03 / 12.0

    tga_target: float = 0.0

    # Optional custom policies/behaviors
    gov_spending_fn: Callable[[int], float] | None = None
    tax_fn: Callable[[int, Dict[str, float]], float] | None = None
    loan_growth_fn: Callable[[int, Dict[str, float]], float] | None = None
    private_loan_growth_fn: Callable[[int, Dict[str, float]], float] | None = None

    # Initial balances by sector/account
    initial: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def resolve_initial(self) -> Dict[str, Dict[str, float]]:
        if self.initial:
            return self.initial
        return {
            "Private": {
                "Deposits": 90.0,
                "Loans": 100.0,
                "PrivateLoansAsset": 0.0,
                "PrivateLoansLiability": 0.0,
                "GovBonds": 0.0,
                "BankDebt": 0.0,
                "Currency": 0.0,
                "NetWorth": 0.0,
            },
            "Banks": {
                "Loans": 100.0,
                "Reserves": 0.0,
                "Deposits": 90.0,
                "BankDebt": 0.0,
                "BankEquity": 0.0,
            },
            "Government": {
                "TGA": 0.0,
                "GovBonds": 0.0,
                "GovEquity": 0.0,
            },
            "CentralBank": {
                "Reserves": 0.0,
                "Currency": 0.0,
                "TGA": 0.0,
                "GovBonds": 0.0,
                "CBEq": 0.0,
            },
        }
