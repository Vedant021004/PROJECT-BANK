from datetime import datetime


class Account:

    def __init__(self, account_number, name, pin, balance=0):
        self.account_number = account_number
        self.name = name
        self.pin = pin
        self.balance = balance
        self.transactions = []

    def check_pin(self, pin):
        return self.pin == pin

    def deposit(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        self.balance += amount

        self.add_transaction("Deposit", amount)

    def withdraw(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.balance:
            raise ValueError("Insufficient balance.")

        self.balance -= amount

        self.add_transaction("Withdrawal", amount)

    def change_pin(self, old_pin, new_pin):

        if old_pin != self.pin:
            raise ValueError("Incorrect current PIN.")

        if len(new_pin) != 4 or not new_pin.isdigit():
            raise ValueError("PIN must contain exactly 4 digits.")

        self.pin = new_pin

    def add_transaction(self, transaction_type, amount):

        transaction = {
            "type": transaction_type,
            "amount": amount,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "balance": self.balance
        }

        self.transactions.append(transaction)

    def show_transactions(self):

        if not self.transactions:
            print("\nNo transactions available.")
            return

        print("\n========== TRANSACTION HISTORY ==========")

        for transaction in self.transactions:

            print(
                f"{transaction['date']} | "
                f"{transaction['type']} | "
                f"₹{transaction['amount']:.2f} | "
                f"Balance: ₹{transaction['balance']:.2f}"
            )

        print("=========================================")

    def show_details(self):

        print("\n========== ACCOUNT DETAILS ==========")
        print(f"Account Holder : {self.name}")
        print(f"Account Number : {self.account_number}")
        print(f"Balance        : ₹{self.balance:.2f}")
        print("=====================================")


class SavingsAccount(Account):

    def withdraw(self, amount):

        if amount > self.balance:
            raise ValueError("Savings account has insufficient balance.")

        self.balance -= amount
        self.add_transaction("Withdrawal", amount)


class CurrentAccount(Account):

    def __init__(self, account_number, name, pin, balance=0):
        super().__init__(
            account_number,
            name,
            pin,
            balance
        )

        self.overdraft_limit = 10000

    def withdraw(self, amount):

        if amount > self.balance + self.overdraft_limit:
            raise ValueError("Overdraft limit exceeded.")

        self.balance -= amount
        self.add_transaction("Withdrawal", amount)


class Bank:

    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def create_account(
        self,
        account_type,
        account_number,
        name,
        pin,
        balance
    ):

        if account_number in self.accounts:
            raise ValueError("Account already exists.")

        if len(pin) != 4 or not pin.isdigit():
            raise ValueError("PIN must contain exactly 4 digits.")

        if balance < 0:
            raise ValueError("Balance cannot be negative.")

        if account_type.lower() == "savings":

            account = SavingsAccount(
                account_number,
                name,
                pin,
                balance
            )

        elif account_type.lower() == "current":

            account = CurrentAccount(
                account_number,
                name,
                pin,
                balance
            )

        else:
            raise ValueError("Invalid account type.")

        self.accounts[account_number] = account

        print("\nAccount created successfully!")

    def login(self, account_number, pin):

        account = self.accounts.get(account_number)

        if account is None:
            return None

        if account.check_pin(pin):
            return account

        return None


class BankingSystem:

    def __init__(self, bank):
        self.bank = bank

    def start(self):

        while True:

            print("\n================================")
            print(f"       {self.bank.name}")
            print("================================")
            print("1. Create Account")
            print("2. Login")
            print("3. Exit")
            print("================================")

            choice = input("Enter choice: ")

            if choice == "1":
                self.create_account()

            elif choice == "2":
                self.login()

            elif choice == "3":
                print("\nThank you for using our bank!")
                break

            else:
                print("\nInvalid choice.")

    def create_account(self):

        print("\n========== CREATE ACCOUNT ==========")

        name = input("Enter name: ")
        account_number = input("Enter account number: ")
        account_type = input("Enter account type (Savings/Current): ")
        pin = input("Create 4-digit PIN: ")

        try:

            balance = float(
                input("Enter initial deposit: ₹")
            )

            self.bank.create_account(
                account_type,
                account_number,
                name,
                pin,
                balance
            )

        except ValueError as error:

            print(f"\nError: {error}")

    def login(self):

        print("\n========== LOGIN ==========")

        account_number = input("Account number: ")
        pin = input("PIN: ")

        account = self.bank.login(
            account_number,
            pin
        )

        if account is None:

            print("\nInvalid account number or PIN.")
            return

        print(f"\nWelcome, {account.name}!")

        self.account_menu(account)

    def account_menu(self, account):

        while True:

            print("\n========== ACCOUNT MENU ==========")
            print("1. Account Details")
            print("2. Check Balance")
            print("3. Deposit")
            print("4. Withdraw")
            print("5. Transaction History")
            print("6. Change PIN")
            print("7. Logout")
            print("==================================")

            choice = input("Enter choice: ")

            try:

                if choice == "1":

                    account.show_details()

                elif choice == "2":

                    print(
                        f"\nCurrent Balance: ₹{account.balance:.2f}"
                    )

                elif choice == "3":

                    amount = float(
                        input("Enter deposit amount: ₹")
                    )

                    account.deposit(amount)

                    print("\nDeposit successful!")

                elif choice == "4":

                    amount = float(
                        input("Enter withdrawal amount: ₹")
                    )

                    account.withdraw(amount)

                    print("\nWithdrawal successful!")

                elif choice == "5":

                    account.show_transactions()

                elif choice == "6":

                    old_pin = input("Enter current PIN: ")
                    new_pin = input("Enter new PIN: ")

                    account.change_pin(
                        old_pin,
                        new_pin
                    )

                    print("\nPIN changed successfully!")

                elif choice == "7":

                    print("\nLogged out successfully.")
                    break

                else:

                    print("\nInvalid choice.")

            except ValueError as error:

                print(f"\nError: {error}")


bank = Bank("SMART BANK")

system = BankingSystem(bank)

system.start()
