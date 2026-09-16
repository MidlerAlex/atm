from __future__ import annotations

import json

from itertools import count
from typing import Callable, Any


class User:
    id_ = count(0, 1)

    def __init__(self, first_name,
                 last_name,
                 patronymic=None,
                 bank_account_number: list = None,
                 cards: list = None) -> None:
        self.id = next(User.id_)
        self._first_name: str = first_name
        self._patronymic: str = patronymic
        self._last_name: str = last_name
        self._bank_accounts: list[BankAccount] = bank_account_number or []
        self._cards: list[Card] = cards or []

    def display_full_name(self) -> None:
        full_name = f"{self._first_name} {self._last_name} {self._patronymic}"
        print(full_name)

    def balance(self, number: str, source_type: str) -> float | None:

        source: dict = {
            "B": BankAccount,
            "C": Card,
        }

        if isinstance(number, str) and number.isnumeric():

            if isinstance(source_type, str) and source_type.upper() in source:

                if source_type.upper() == "B":
                    return self.get_bank_account(number)

                if source_type.upper() == "C":
                    return self.get_card(number)
            raise ValueError("Неверный источник проверки баланса")

        raise ValueError("Необходимо указать номер")

    def get_card(self, card_number: str) -> Card:
        for card in self._cards:
            if card.card_number == card_number:
                return card
        raise ValueError("Карта не существует")

    def add_card(self, card: Card) -> None:
        if card in self._cards:
            raise ValueError("Данная карта уже привязана к пользователю")
        self._cards.append(card)

    def delete_card(self, card: Card) -> None:
        if card not in self._cards:
            raise ValueError("Карта не принадлежит пользователю")
        self._cards.remove(card)

    def get_bank_account(self, account_number: str) -> BankAccount:
        for bank_account in self._bank_accounts:
            if bank_account.account_number == account_number:
                return bank_account
        raise ValueError("Номер счета не существует")

    def add_bank_account(self, bank_account: BankAccount) -> None:
        if bank_account in self._bank_accounts:
            raise ValueError("Данный банковский счет уже привязана к пользователю")

        self._bank_accounts.append(bank_account)

    def delete_bank_account(self, bank_account: BankAccount) -> None:
        if bank_account not in self._bank_accounts:
            raise ValueError("Банковский счет не принадлежит пользователю")
        self._bank_accounts.remove(bank_account)

    def card_belong_user(self, card_number) -> Card | None:
        for card in self._cards:
            if card.card_number == card_number:
                return card
        return None

    def bank_account_belong_user(self, bank_account: BankAccount) -> bool:
        for i in self._bank_accounts:
            if i.account_number == bank_account.account_number:
                return True
        return False

    def check_pin_code(self, card_number, pin_code: str) -> bool:
        if isinstance(card_number, str) and card_number.isnumeric():
            user_card = self.card_belong_user(card_number)
            if user_card is None:
                raise ValueError("Карты не существует")
            if card.pin != pin_code:
                raise ValueError("Неверный пин-кол")
            return True
        raise ValueError("Неверный номер карты")

    def card_to_card_transfer(self, amount: float, write_off_card_number: str, top_up_card_number: str) -> None:

        user_write_off_card_number = self.get_card(write_off_card_number)
        user_top_up_card_number = self.get_card(top_up_card_number)

        if user_write_off_card_number is not None and user_top_up_card_number is not None:

            try:
                amount = float(amount)
            except ValueError:
                print("Необходимо указать положительное число")

            if amount < 0:
                print("Сумма должна быть больше 0")

            if user_write_off_card_number.card_number == user_top_up_card_number.card_number:
                print("Необходимо указать разные карты для перевода")

            if write_off_card.balance < amount:
                print("Не хватает средств для снятия")

            user_write_off_card_number.write_off_card(amount)
            user_top_up_card_number.top_up_card(amount)


        else:
            print("Необходимо указать номер карты")


class Card:

    def __init__(self, card_holder: str, pin: str):
        self.card_number = None
        self.expiration_date = None
        self.card_holder = card_holder
        self.cvv = None
        self._bank_account: BankAccount = None
        self.pin = pin

    @property
    def bank_account(self) -> BankAccount:
        return self._bank_account

    def write_off_card(self, amount) -> None:
        self._bank_account.write_off_account(amount)

    def put_money(self, amount) -> None:
        self._bank_account.put_money(amount)

    @property
    def balance(self):
        return self._bank_account.balance


class BankAccount:
    def __init__(self):
        self.account_number = None
        self._balance: float = 0.0
        self.type = None

    @property
    def balance(self) -> float:
        return self._balance

    def write_off_account(self, amount: float) -> None:
        try:
            balance_ = float(amount)
        except ValueError:
            print("Требуется передать число")

        if balance_ <= 0.0:
            print("Сумма должна быть положительной")

        self._balance -= balance_

    def put_money(self, amount: float) -> None:
        try:
            balance_ = float(value)
        except ValueError:
            print("Требуется передать число")

        if balance_ <= 0.0:
            print("Сумма должна быть положительной")

        self._balance += amount


def transfer(
        source: BankAccount,
        destination: BankAccount,
        amount: float,
) -> None:
    source.write_off_account(amount)
    destination.put_money(amount)


def create_json(file_name: str, data: dict[str, float]) -> None:
    with open(file_name, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def request_id() -> dict[str, Any] | None:
    user_id = int(input("Введите ваш id: "))

    if not isinstance(user_id, int) or user_id < 0:
        raise ValueError("Неверный id")

    with open("db.json", "r") as file:
        db_json = json.load(file)

    for user in db_json:
        if user_id == user["id"]:
            return user

    raise ValueError("Пользователь не найден")


def request_pin_code(pin_code) -> None:
    user_pin_code = input("Введите ваш пин-код: ")

    if user_pin_code.isdigit() and len(user_pin_code) == 4:
        if user_pin_code == pin_code:
            return
        raise ValueError("Неверный пин-код")
    raise ValueError("Пин-код должен состоять из 4 цифр")


def request_money(amount_money: float) -> float:
    while True:
        user_request = input("Введите сумму для снятия: ")
        try:
            user_request = float(user_request)

        except ValueError:
            print("Требуется ввести число")
            continue

        if user_request <= 0:
            print("Сумма должна быть положительной")

        elif user_request > amount_money:
            print("Недостаточно средств")
        else:
            amount_money -= user_request
            print(f"Вы сняли со счета: {user_request:.2f}")
            print(f"Остаток по счету: {amount_money:.2f}")
            return amount_money


def put_money(amount_money: float) -> float:
    while True:
        user_request = input("Введите сумму для пополнения: ")
        try:
            user_request = float(user_request)

        except ValueError:
            print("Требуется ввести число")
            continue

        if user_request <= 0:
            print("Сумма должна быть положительной")

        else:
            amount_money += user_request
            print(f"Вы пополнили счет на сумму: {user_request:.2f}")
            print(f"Остаток по счету: {amount_money:.2f}")
            return amount_money


def balance(amount_money: float) -> float:
    print(f"Баланс счета: {amount_money:.2f}")
    print()
    return amount_money


def main() -> None:
    is_authorized: bool = False
    operation: dict[int, Callable[[float], float]] = {
        1: request_money,
        2: put_money,
        3: balance,
    }

    while True:

        if not is_authorized:
            try:
                user = request_id()
                pin_code = user["pin_code"]
                amount_money = user["amount_money"]

                request_pin_code(pin_code)
                is_authorized = True
            except ValueError as e:
                print(e)
                continue
        print("Доступные операции:\n 1 - Снятие со счета\n 2 - Пополнение счета\n 3 - Баланс\n 0 - Завершить программу")
        print()

        try:
            user_request = int(input("Введите номер операции: "))


        except ValueError:
            print("Требуется указать цифру операции")
            continue

        if user_request == 0:
            print("Работа завершена")
            return

        if user_request not in operation:
            print("Нет такой операции")
            print()
            continue

        amount_money = operation[user_request](amount_money)
        user["amount_money"] = amount_money

        with open("db.json", "r") as file:
            db_json = json.load(file)
            for i, u in enumerate(db_json):
                if user["id"] == u["id"]:
                    db_json[i] = user

        with open("db.json", "w") as file:
            json.dump(db_json, file, indent=4)


if __name__ == '__main__':
    # users = [
    #     {
    #         "id": 1,
    #         "amount_money": 1000,
    #         "pin_code": "1234",
    #     },
    #     {
    #         "id": 2,
    #         "amount_money": 2000,
    #         "pin_code": "4321",
    #     },
    #     {
    #         "id": 3,
    #         "amount_money": 5000,
    #         "pin_code": "6789",
    #     }
    # ]
    # file_name = 'db.json'
    # create_json(file_name, users)
    main()
