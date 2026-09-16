import json
from typing import Callable, Any


class User:

    def __init__(self, first_name,
                 last_name,
                 patronymic=None,
                 bank_account_number: list = None,
                 cars: list = None) -> None:
        self._first_name: str = first_name
        self._patronymic: str = patronymic
        self._last_name: str = last_name
        self._bank_accounts: list[BankAccount] = bank_account_number or []
        self._cards: list[Card] = bank_account_number or []


class Card:

    def __init__(self, card_holder: str, pin: str):
        self._card_number = None
        self._expiration_date = None
        self._card_holder = card_holder
        self._cvv = None
        self._bank_account = None
        self._pin = pin


class BankAccount:
    def __init__(self):
        self.account_number = None
        self.balance = None
        self.type = None


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
