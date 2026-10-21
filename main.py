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


"""
1. Завел флаг авторизации, список операций, текущий счет - Подготовка
2. Проверка авторизации. Если нет авторизации, то авторизует: 
    Спрашивает пин, проверяет пин, авторизует
    иначе сообщает об ошибке и пытает авторизоваться снова - Авторизация
3. Выбор счета. Если не выбран, то показать счета, проверить, запоминание в переменную
4. Меню. Показать меню, спросить номер операции
5.Выполнить операцию, вызвать метод связанный с номером. Выполнение
6. Сохранить изменения. Прочитать db.json, найти пользователя, сохранить изменения
"""


def authorize() -> dict[str, Any]:
    while True:
        try:
            user = request_id()
            pin_code = user["pin_code"]
            request_pin_code(pin_code)
            return user
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

        user_bank_accounts = user["bank_accounts"]
        for number, bank_account in enumerate(user_bank_accounts, 1):
            print(f"{number}. Номер счета: {bank_account["id"]}, баланс: {bank_account['balance']}")

        print()
        selected_bank_account = user_bank_accounts[int(input("Укажите номер счета: ")) - 1]

        return selected_bank_account

    return current_bank_account


def choice_operation(operation: dict[int, Callable[[float], float]]) -> int:
    print("Доступные операции:\n 1 - Снятие со счета\n 2 - Пополнение счета\n 3 - Баланс\n 0 - Завершить программу")
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


def execute_operation(operation: dict[int, Callable[[float], float]], user_request, current_bank_account) -> float:
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


def main() -> None:
    user: dict[str, Any] = authorize()
    operation: dict[int, Callable[[float], float]] = get_operation()
    current_bank_account = None
    if current_bank_account is None:
        current_bank_account = choice_bank_account(current_bank_account, user)

    user_request = choice_operation(operation)
    while user_request:
        balance = execute_operation(operation, user_request, current_bank_account)
        save(user, current_bank_account, balance)
        user_request = choice_operation(operation)
    print("Работа завершена!")


if __name__ == '__main__':
    main()
