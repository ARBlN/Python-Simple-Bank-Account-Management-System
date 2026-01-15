# Bank Account Management System

from time import perf_counter, strftime, localtime
from functools import wraps



# Decorators 

class TimeMeasure:
    def __call__(self, fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            start = perf_counter()
            result = fn(*args, **kwargs)
            elapsed_ms = (perf_counter() - start) * 1000
            print(f"[time] {fn.__name__}: {elapsed_ms:.3f} ms")
            return result
        return inner


class SufficientBalance:
    def __call__(self, fn):
        @wraps(fn)
        def inner(self, amount, *args, **kwargs):
            if self.is_account_closed():
                print("Withdrawal denied: account is closed.")
                return
            try:
                amt = float(amount)
            except (TypeError, ValueError):
                print("Withdrawal denied: amount must be numeric.")
                return
            if amt <= 0:
                print("Withdrawal denied: amount must be positive.")
                return
            if amt > self.balance:
                print("Withdrawal denied: insufficient funds.")
                return
            return fn(self, amt, *args, **kwargs)  # pass validated float
        return inner


# Core class

class BankAccount:
    _next_number = 1000  

    def __init__(self, initial_balance=0.0):
        self.account_number = BankAccount._next_number
        BankAccount._next_number += 1

        self.balance = float(initial_balance)
        self._transactions = []  # list of dicts
        self._closed = False

    # helpers
    @staticmethod
    def _now():
        return strftime("%Y-%m-%d %H:%M:%S", localtime())

    def _log(self, tx_type, amount):
        self._transactions.append({
            "timestamp": self._now(),
            "type": tx_type,                # "deposit" or "withdrawal"
            "amount": float(amount),
            "balance_after": float(self.balance),
        })

    # operations
    @TimeMeasure()  # timing of deposit
    def deposit(self, amount):
        if self.is_account_closed():
            print("Deposit denied: account is closed.")
            return
        try:
            amt = float(amount)
        except (TypeError, ValueError):
            print("Deposit denied: amount must be numeric.")
            return
        if amt <= 0:
            print("Deposit denied: amount must be positive.")
            return
        self.balance += amt
        self._log("deposit", amt)
        print(f"Deposited {amt:.2f}. Balance: {self.balance:.2f}")

    @TimeMeasure()       # timing of withdrawal
    @SufficientBalance() # guard decorator for withdrawal
    def withdraw(self, amount):
        self.balance -= amount
        self._log("withdrawal", amount)
        print(f"Withdrew {amount:.2f}. Balance: {self.balance:.2f}")

    # reports
    def get_balance(self):
        return self.balance

    def get_transactions(self):
        return list(self._transactions) 

    def print_statement(self):
        print("\n=== ACCOUNT STATEMENT ===")
        print(f"Account: {self.account_number}")
        print("-------------------------------")
        if not self._transactions:
            print("(no transactions)")
        else:
            for tx in self._transactions:
                ts = tx["timestamp"]
                kind = tx["type"]
                amt = tx["amount"]
                bal = tx["balance_after"]
                print(f"{ts} | {kind:<10} | amount: {amt:>10.2f} | balance: {bal:>10.2f}")
        print("-------------------------------")
        print(f"Current balance: {self.balance:.2f}")
        print("===========================\n")

    def print_summary(self):
        print("\n=== ACCOUNT SUMMARY ===")
        print(f"Account number : {self.account_number}")
        print(f"Current balance: {self.balance:.2f}")
        print(f"# transactions : {len(self._transactions)}")
        print("=======================\n")

    # lifecycle
    def close_account(self):
        self.balance = 0.0
        self._transactions.clear()
        self._closed = True
        print("Account closed. Balance set to 0. Transaction history cleared.")

    def is_account_closed(self):
        return self._closed



# Menu-driven interface

def _prompt_float(msg):
    s = input(msg).strip()
    try:
        return float(s)
    except ValueError:
        return None

def main():
    account = None  

    MENU = """
1 Open a new account
2 Deposit money into your account
3 Withdraw money from your account
4 Balance inquiry
5 Retrieve transaction history
6 Print account statement
7 Print account summary
8 Close account
9 Check if account is closed
0 Quit
Choice: """

    while True:
        choice = input(MENU).strip()

        if choice == "1":
            if account is not None and not account.is_account_closed():
                print("An open account already exists.")
                continue
            init = _prompt_float("Initial balance (0 if none): ")
            if init is None or init < 0:
                print("Invalid amount.")
                continue
            account = BankAccount(initial_balance=init)
            print(f"Account opened. Number: {account.account_number}. Balance: {account.balance:.2f}")

        elif choice == "2":
            if account is None:
                print("Open an account first.")
                continue
            amount = _prompt_float("Deposit amount: ")
            account.deposit(amount)

        elif choice == "3":
            if account is None:
                print("Open an account first.")
                continue
            amount = _prompt_float("Withdrawal amount: ")
            account.withdraw(amount)

        elif choice == "4":
            if account is None:
                print("Open an account first.")
                continue
            print(f"Current balance: {account.get_balance():.2f}")

        elif choice == "5":
            if account is None:
                print("Open an account first.")
                continue
            txs = account.get_transactions()
            if not txs:
                print("(no transactions)")
            else:
                for tx in txs:
                    print(tx)

        elif choice == "6":
            if account is None:
                print("Open an account first.")
                continue
            account.print_statement()

        elif choice == "7":
            if account is None:
                print("Open an account first.")
                continue
            account.print_summary()

        elif choice == "8":
            if account is None:
                print("Open an account first.")
                continue
            account.close_account()

        elif choice == "9":
            if account is None:
                print("Open an account first.")
                continue
            print("Account is closed." if account.is_account_closed() else "Account is open.")

        elif choice == "0":
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()