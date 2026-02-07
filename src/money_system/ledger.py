from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


CATEGORY_SIGN = {
    "asset": 1.0,
    "liability": -1.0,
    "equity": -1.0,
}


@dataclass
class Account:
    name: str
    category: str
    balance: float = 0.0

    def apply(self, delta: float) -> None:
        self.balance += delta


@dataclass
class SectorLedger:
    name: str
    accounts: Dict[str, Account] = field(default_factory=dict)

    def apply(self, account_name: str, delta: float) -> None:
        if account_name not in self.accounts:
            raise KeyError(f"Unknown account '{account_name}' in sector '{self.name}'")
        self.accounts[account_name].apply(delta)

    def assets_total(self) -> float:
        return sum(a.balance for a in self.accounts.values() if a.category == "asset")

    def liabilities_total(self) -> float:
        return sum(a.balance for a in self.accounts.values() if a.category == "liability")

    def equity_total(self) -> float:
        return sum(a.balance for a in self.accounts.values() if a.category == "equity")

    def net_position(self) -> float:
        return self.assets_total() - self.liabilities_total()

    def recompute_equity(self) -> None:
        equity_accounts = [a for a in self.accounts.values() if a.category == "equity"]
        if not equity_accounts:
            return
        residual = self.assets_total() - self.liabilities_total()
        split = residual / len(equity_accounts)
        for a in equity_accounts:
            a.balance = split

    def assert_balanced(self, tol: float = 1e-6) -> None:
        assets = self.assets_total()
        liabilities = self.liabilities_total()
        equity = self.equity_total()
        if abs(assets - liabilities - equity) > tol:
            raise ValueError(
                f"Sector '{self.name}' unbalanced: A={assets:.6f} L={liabilities:.6f} E={equity:.6f}"
            )


@dataclass
class Posting:
    sector: str
    account: str
    amount: float


@dataclass
class Transaction:
    name: str
    postings: List[Posting]
    meta: Dict[str, float] = field(default_factory=dict)

    def total(self, ledger: "Ledger") -> float:
        total = 0.0
        for p in self.postings:
            account = ledger.sectors[p.sector].accounts[p.account]
            sign = CATEGORY_SIGN[account.category]
            total += p.amount * sign
        return total


class Ledger:
    def __init__(self, sectors: Dict[str, SectorLedger]):
        self.sectors = sectors
        self.transactions: List[Transaction] = []

    def apply(self, tx: Transaction, tol: float = 1e-6) -> None:
        imbalance = tx.total(self)
        if abs(imbalance) > tol:
            raise ValueError(f"Transaction '{tx.name}' unbalanced by {imbalance:.6f}")
        for p in tx.postings:
            self.sectors[p.sector].apply(p.account, p.amount)
        self.transactions.append(tx)

    def recompute_equity(self) -> None:
        for sector in self.sectors.values():
            sector.recompute_equity()
            sector.assert_balanced()

    def snapshot(self) -> Dict[str, float]:
        data: Dict[str, float] = {}
        for sector_name, sector in self.sectors.items():
            for account in sector.accounts.values():
                key = f"{sector_name}:{account.name}"
                data[key] = account.balance
        return data


def default_chart(initial: Dict[str, Dict[str, float]]) -> Dict[str, SectorLedger]:
    def make_sector(name: str, account_defs: Dict[str, str]) -> SectorLedger:
        accounts = {
            acc_name: Account(acc_name, category, initial.get(name, {}).get(acc_name, 0.0))
            for acc_name, category in account_defs.items()
        }
        return SectorLedger(name=name, accounts=accounts)

    return {
        "Private": make_sector(
            "Private",
            {
                "Deposits": "asset",
                "Loans": "liability",
                "GovBonds": "asset",
                "Currency": "asset",
                "NetWorth": "equity",
            },
        ),
        "Banks": make_sector(
            "Banks",
            {
                "Loans": "asset",
                "Reserves": "asset",
                "Deposits": "liability",
                "BankEquity": "equity",
            },
        ),
        "Government": make_sector(
            "Government",
            {
                "TGA": "asset",
                "GovBonds": "liability",
                "GovEquity": "equity",
            },
        ),
        "CentralBank": make_sector(
            "CentralBank",
            {
                "Reserves": "liability",
                "Currency": "liability",
                "TGA": "liability",
                "GovBonds": "asset",
                "CBEq": "equity",
            },
        ),
    }


def build_default_ledger(initial: Dict[str, Dict[str, float]]) -> Ledger:
    ledger = Ledger(default_chart(initial))
    ledger.recompute_equity()
    return ledger
