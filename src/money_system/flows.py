from __future__ import annotations

from typing import List

from .ledger import Posting, Transaction


def tx_government_spending(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("gov_spending_zero", [])
    return Transaction(
        "government_spending",
        [
            Posting("Private", "Deposits", amount),
            Posting("Banks", "Deposits", amount),
            Posting("Banks", "Reserves", amount),
            Posting("CentralBank", "Reserves", amount),
            Posting("CentralBank", "TGA", -amount),
            Posting("Government", "TGA", -amount),
        ],
        meta={"amount": amount},
    )


def tx_taxes(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("taxes_zero", [])
    return Transaction(
        "taxes",
        [
            Posting("Private", "Deposits", -amount),
            Posting("Banks", "Deposits", -amount),
            Posting("Banks", "Reserves", -amount),
            Posting("CentralBank", "Reserves", -amount),
            Posting("CentralBank", "TGA", amount),
            Posting("Government", "TGA", amount),
        ],
        meta={"amount": amount},
    )


def tx_loan_creation(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("loan_creation_zero", [])
    return Transaction(
        "loan_creation",
        [
            Posting("Banks", "Loans", amount),
            Posting("Private", "Loans", amount),
            Posting("Banks", "Deposits", amount),
            Posting("Private", "Deposits", amount),
        ],
        meta={"amount": amount},
    )


def tx_loan_repayment(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("loan_repayment_zero", [])
    return Transaction(
        "loan_repayment",
        [
            Posting("Private", "Deposits", -amount),
            Posting("Banks", "Deposits", -amount),
            Posting("Banks", "Loans", -amount),
            Posting("Private", "Loans", -amount),
        ],
        meta={"amount": amount},
    )


def tx_private_loan_creation(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("private_loan_creation_zero", [])
    return Transaction(
        "private_loan_creation",
        [
            Posting("Private", "PrivateLoansAsset", amount),
            Posting("Private", "PrivateLoansLiability", amount),
        ],
        meta={"amount": amount},
    )


def tx_private_loan_repayment(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("private_loan_repayment_zero", [])
    return Transaction(
        "private_loan_repayment",
        [
            Posting("Private", "PrivateLoansAsset", -amount),
            Posting("Private", "PrivateLoansLiability", -amount),
        ],
        meta={"amount": amount},
    )


def tx_interest_on_loans(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("interest_loans_zero", [])
    return Transaction(
        "interest_on_loans",
        [
            Posting("Private", "Deposits", -amount),
            Posting("Banks", "Deposits", -amount),
        ],
        meta={"amount": amount},
    )


def tx_interest_on_deposits(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("interest_deposits_zero", [])
    return Transaction(
        "interest_on_deposits",
        [
            Posting("Private", "Deposits", amount),
            Posting("Banks", "Deposits", amount),
        ],
        meta={"amount": amount},
    )


def tx_interest_on_reserves(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("interest_reserves_zero", [])
    return Transaction(
        "interest_on_reserves",
        [
            Posting("Banks", "Reserves", amount),
            Posting("CentralBank", "Reserves", amount),
        ],
        meta={"amount": amount},
    )


def tx_interest_on_bonds(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("interest_bonds_zero", [])
    return Transaction(
        "interest_on_bonds",
        [
            Posting("Private", "Deposits", amount),
            Posting("Banks", "Deposits", amount),
            Posting("Banks", "Reserves", amount),
            Posting("CentralBank", "Reserves", amount),
            Posting("CentralBank", "TGA", -amount),
            Posting("Government", "TGA", -amount),
        ],
        meta={"amount": amount},
    )


def tx_bond_issue(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("bond_issue_zero", [])
    return Transaction(
        "bond_issue",
        [
            Posting("Private", "Deposits", -amount),
            Posting("Banks", "Deposits", -amount),
            Posting("Banks", "Reserves", -amount),
            Posting("CentralBank", "Reserves", -amount),
            Posting("CentralBank", "TGA", amount),
            Posting("Government", "TGA", amount),
            Posting("Government", "GovBonds", amount),
            Posting("Private", "GovBonds", amount),
        ],
        meta={"amount": amount},
    )


def tx_bond_sale_to_cb(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("bond_sale_to_cb_zero", [])
    return Transaction(
        "bond_sale_to_cb",
        [
            Posting("Government", "GovBonds", amount),
            Posting("CentralBank", "GovBonds", amount),
            Posting("CentralBank", "TGA", amount),
            Posting("Government", "TGA", amount),
        ],
        meta={"amount": amount},
    )


def tx_bank_debt_issue(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("bank_debt_issue_zero", [])
    return Transaction(
        "bank_debt_issue",
        [
            Posting("Private", "Deposits", -amount),
            Posting("Banks", "Deposits", -amount),
            Posting("Private", "BankDebt", amount),
            Posting("Banks", "BankDebt", amount),
        ],
        meta={"amount": amount},
    )


def tx_bank_debt_repayment(amount: float) -> Transaction:
    if amount == 0:
        return Transaction("bank_debt_repayment_zero", [])
    return Transaction(
        "bank_debt_repayment",
        [
            Posting("Private", "Deposits", amount),
            Posting("Banks", "Deposits", amount),
            Posting("Private", "BankDebt", -amount),
            Posting("Banks", "BankDebt", -amount),
        ],
        meta={"amount": amount},
    )


def select_transactions(txs: List[Transaction]) -> List[Transaction]:
    return [tx for tx in txs if tx.postings]
