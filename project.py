
from abc import ABC, abstractmethod
from datetime import datetime


class Account(ABC):

    def __init__(self, account_number, holder_name, pin, balance=0):
        self._account_number = account_number
        self._holder_name = holder_name
        self._pin = pin
        self._balance = balance
        self._transactions = []

    @property
    def account_number(self):
        return self._account_number

    @property
    def holder_name(self):
        return self._holder_name

    @property
    def balance(self):
        return self._balance

    def verify_pin(self, pin):
        return self._pin == pin

    def change_pin(self, old_pin, new_pin):
        if not self.verify_pin(old_pin):
            raise ValueError("Incorrect current PIN.")

        if not new_pin.isdigit() or len(new_pin) != 4:
            raise ValueError("PIN must contain exactly 4 digits.")

        self._pin = new_pin
        return True

    def deposit(self, amount):

        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._balance += amount

        self._add_transaction(
            "DEPOSIT",
            amount
        )

    @abstractmethod
    def withdraw(self, amount):
        pass

    def _add_transaction(self, transaction_type, amount):

        transaction = {
            "type": transaction_type,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "balance": self._balance
        }

        self._transactions.append(transaction)

    def transaction_history(self):

        if not self._transactions:
            print("\nNo transactions found.")
            return

        print("\n========== TRANSACTION HISTORY ==========")

        for transaction in self._transactions:
            print(
                f"{transaction['date']} | "
                f"{transaction['type']} | "
                f"₹{transaction['amount']:.2f} | "
                f"Balance: ₹{transaction['balance']:.2f}"
            )

        print("=========================================")

    def display_account(self):

        print("\n========== ACCOUNT DETAILS ==========")
        print(f"Account Holder : {self._holder_name}")
        print(f"Account Number : {self._account_number}")
        print(f"Account Type   : {self.__class__.__name__}")
        print(f"Balance        : ₹{self._balance:.2f}")
        print("=====================================")


class SavingsAccount(Account):

    def withdraw(self, amount):

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self._balance:
            raise ValueError("Insufficient balance.")

        self._balance -= amount

        self._add_transaction(
            "WITHDRAW",
            amount
        )


class CurrentAccount(Account):

    OVERDRAFT_LIMIT = 10000

    def withdraw(self, amount):

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self._balance + self.OVERDRAFT_LIMIT:
            raise ValueError("Withdrawal exceeds overdraft limit.")

        self._balance -= amount

        self._add_transaction(
            "WITHDRAW",
            amount
        )


class Bank:

    def __init__(self, bank_name):
        self.bank_name = bank_name
        self._accounts = {}

    def create_account(
        self,
        account_type,
        account_number,
        holder_name,
        pin,
        initial_balance=0
    ):

        if account_number in self._accounts:
            raise ValueError("Account already exists.")

        if not pin.isdigit() or len(pin) != 4:
            raise ValueError("PIN must contain exactly 4 digits.")

        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        if account_type.lower() == "savings":

            account = SavingsAccount(
                account_number,
                holder_name,
                pin,
                initial_balance
            )

        elif account_type.lower() == "current":

            account = CurrentAccount(
                account_number,
                holder_name,
                pin,
                initial_balance
            )

        else:
            raise ValueError("Invalid account type.")

        self._accounts[account_number] = account

        return account

    def get_account(self, account_number):

        return self._accounts.get(account_number)

    def authenticate(self, account_number, pin):

        account = self.get_account(account_number)

        if account is None:
            return None

        if account.verify_pin(pin):
            return account

        return None


class BankingApplication:

    def __init__(self, bank):
        self.bank = bank
        self.current_account = None

    def run(self):

        while True:

            print("\n")
            print("======================================")
            print(f"       {self.bank.bank_name}")
            print("======================================")
            print("1. Create Account")
            print("2. Login")
            print("3. Exit")
            print("======================================")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.create_account()

            elif choice == "2":
                self.login()

            elif choice == "3":
                print("\nThank you for banking with us!")
                break

            else:
                print("\nInvalid choice.")

    def create_account(self):

        print("\n========== CREATE ACCOUNT ==========")

        name = input("Enter account holder name: ")
        account_number = input("Enter account number: ")
        account_type = input("Account type (Savings/Current): ")
        pin = input("Create 4-digit PIN: ")

        try:

            initial_balance = float(
                input("Enter initial deposit: ₹")
            )

            self.bank.create_account(
                account_type,
                account_number,
                name,
                pin,
                initial_balance
            )

            print("\nAccount created successfully!")

        except ValueError as error:

            print(f"\nError: {error}")

    def login(self):

        print("\n========== LOGIN ==========")

        account_number = input("Account Number: ")
        pin = input("PIN: ")

        account = self.bank.authenticate(
            account_number,
            pin
        )

        if account is None:

            print("\nInvalid account number or PIN.")
            return

        self.current_account = account

        print(
            f"\nWelcome, {account.holder_name}!"
        )

        self.account_menu()

    def account_menu(self):

        while True:

            print("\n========== BANKING MENU ==========")
            print("1. Account Details")
            print("2. Check Balance")
            print("3. Deposit Money")
            print("4. Withdraw Money")
            print("5. Transaction History")
            print("6. Change PIN")
            print("7. Logout")
            print("==================================")

            choice = input("Enter your choice: ")

            try:

                if choice == "1":

                    self.current_account.display_account()

                elif choice == "2":

                    print(
                        f"\nCurrent Balance: "
                        f"₹{self.current_account.balance:.2f}"
                    )

                elif choice == "3":

                    amount = float(
                        input("Enter deposit amount: ₹")
                    )

                    self.current_account.deposit(amount)

                    print(
                        f"\n₹{amount:.2f} deposited successfully."
                    )

                elif choice == "4":

                    amount = float(
                        input("Enter withdrawal amount: ₹")
                    )

                    self.current_account.withdraw(amount)

                    print(
                        f"\n₹{amount:.2f} withdrawn successfully."
                    )

                elif choice == "5":

                    self.current_account.transaction_history()

                elif choice == "6":

                    old_pin = input(
                        "Enter current PIN: "
                    )

                    new_pin = input(
                        "Enter new 4-digit PIN: "
                    )

                    self.current_account.change_pin(
                        old_pin,
                        new_pin
                    )

                    print("\nPIN changed successfully.")

                elif choice == "7":

                    print("\nLogged out successfully.")
                    self.current_account = None
                    break

                else:

                    print("\nInvalid choice.")

            except ValueError as error:

                print(f"\nError: {error}")


bank = Bank("SMART BANK")

app = BankingApplication(bank)

app.run()
