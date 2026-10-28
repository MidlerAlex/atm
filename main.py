import os
import json
from typing import Callable, Any

"""
Интерфейс - диалог, вызывать логику
Класс диалог
Привет
Вставь карту
[Логика] Проверить карту
Если ок - следующий вопрос
База данных
Логика
проверяет карту

Создать админский код
Создать код диалога
"""


def get_clients(client_id=None) -> dict[str, Any] | None:
    with open("db.json", "r") as file:
        db_json = json.load(file)

    if client_id is not None:
        for client in db_json:
            if client["id"] == client_id:
                return client

        return None

    return db_json


def request_card_number(client: dict[str, Any]) -> str | None:
    card_number = input("Введите номер банковской карты: ")

    while True:
        if not card_number.isdigit():
            print("Номер должен состоять только из цифр 0-9")
        else:
            for card in client["cards"]:
                if card["number"] == card_number:
                    request_pin_code(card["pin_code"])
                    return card

            print("Неверный номер карты")

        card_number = input("Введите номер банковской карты: ")


def request_id() -> dict[str, Any] | None:
    user_id = int(input("Введите ваш id: "))

    if not isinstance(user_id, int) or user_id < 0:
        raise ValueError("Неверный id")

    client = get_clients(user_id)
    if not client:
        raise ValueError("Пользователь не найден")
    return client


def check_pin_code_condition(user_pin_code: str, pin_code: str) -> bool:
    return (user_pin_code.isdigit()
            and len(user_pin_code) == 4
            and user_pin_code == pin_code)


def request_pin_code(pin_code) -> None:
    max_attempt = 3

    while max_attempt > 0:
        user_pin_code = input("Введите ваш пин-код: ")

        if not check_pin_code_condition(user_pin_code, pin_code):
            print("Неверный пин-код")
            max_attempt -= 1
            continue
        return
    raise ValueError("Превышен лимит ввода пин-кода")


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


def authorize() -> dict[str, Any]:
    while True:
        try:
            client = request_id()
            return client
        except ValueError:

            continue


def get_operation() -> dict[int, Callable[[float], float]]:
    return {
        1: request_money,
        2: put_money,
        3: balance,
    }


def choice_bank_account(current_bank_account: str | None, user) -> str:
    if current_bank_account is None:
        print()
        print("Выберете номер счета для проведения операций:")
        while True:
            user_bank_accounts = user["bank_accounts"]
            for number, bank_account in enumerate(user_bank_accounts, 1):
                print(f"{number}. Номер счета: {bank_account["id"]}, баланс: {bank_account['balance']}")

            print()
            try:
                selected_bank_account = user_bank_accounts[int(input("Укажите номер счета: ")) - 1]

                return selected_bank_account
            except IndexError:
                print("Укажите корректный номер банковского счета. Требуется указать цифру до точки")
                continue

    return current_bank_account


def choice_operation(operation: dict[int, Callable[[float], float]]) -> int:
    print(
        "Доступные операции:\n 1 - Снятие со счета\n 2 - Пополнение счета\n 3 - Баланс\n 0 - Вернуться в главное меню")
    print()

    while True:
        try:
            user_request = int(input("Введите номер операции: "))

        except ValueError:
            print("Требуется указать цифру операции")
            continue

        if user_request == 0:
            return 0

        if user_request not in operation:
            print("Нет такой операции")
            print()
            continue

        return user_request


def execute_operation(operation: dict[int, Callable[[float], float]],
                      user_request,
                      current_bank_account
                      ) -> float:
    balance = current_bank_account['balance']
    executed_operation = operation[user_request]
    amount_money = executed_operation(balance)
    return amount_money


def save(user, current_bank_account, balance) -> None:
    change_user = user
    change_bank_account = current_bank_account
    new_balance = balance
    for bank_account in change_user["bank_accounts"]:
        if bank_account['id'] == change_bank_account["id"]:
            bank_account["balance"] = new_balance

    temp_db_json = "db_tmp.json"

    with open("db.json", "r") as file:
        db_json = json.load(file)

    for i, u in enumerate(db_json):
        if user["id"] == u["id"]:
            db_json[i] = user

    with open(temp_db_json, "w") as file:
        json.dump(db_json, file, indent=4)

    os.replace(temp_db_json, "db.json")


def menu() -> int:
    print("Выберите вид операций: ")
    print("1 - Операции по карте")
    print("2 - Операции с банковскими счетами")
    print("0 - Завершить работу")
    while True:
        try:
            user_request = int(input("Введите номер операции: "))

        except ValueError:
            print("Требуется указать цифру операции")
            continue

        if user_request == 0:
            return 0

        if user_request > 2:
            print("Нет такой операции")
            continue

        return user_request


def bank_account_flow(client, operation, input_current_bank_account=None):
    current_bank_account = input_current_bank_account
    if current_bank_account is None:
        current_bank_account = choice_bank_account(current_bank_account, client)

    client_request = choice_operation(operation)
    while client_request:
        balance = execute_operation(operation, client_request, current_bank_account)
        save(client, current_bank_account, balance)
        client_request = choice_operation(operation)


def card_flow(client, card, operation):
    bank_account_id = card["bank_account_id"]
    current_bank_account = None

    for bank_account in client["bank_accounts"]:
        if bank_account["id"] == bank_account_id:
            current_bank_account = bank_account

    bank_account_flow(client, operation, current_bank_account)


def main() -> None:
    client: dict[str, Any] = authorize()
    try:
        card = request_card_number(client)
    except ValueError as value_error:
        print(str(value_error))
        print("Обратитесь позже")
        return

    operation: dict[int, Callable[[float], float]] = get_operation()
    user_request = menu()
    while user_request:
        if user_request == 1:
            card_flow(client, card, operation)

        elif user_request == 2:
            bank_account_flow(client, operation)

        user_request = menu()
    print("Работа завершена!")


if __name__ == '__main__':
    main()
