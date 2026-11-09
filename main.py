import os
import json
from typing import Callable, Any


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


def request_money(amount_money: float, input_amount: float | None = None) -> float:
    while True:
        if input_amount is None:
            user_request = input("Введите сумму для снятия: ")
        else:
            user_request = input_amount
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


def put_money(amount_money: float, input_amount: float | None = None) -> float:
    while True:
        if input_amount is None:
            user_request = input("Введите сумму для пополнения: ")
        else:
            user_request = input_amount
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
    max_attempt = 3
    while max_attempt > 0:
        try:
            client = request_id()
            return client
        except ValueError:
            print("Ошибка авторизации")
            max_attempt -= 1
            continue
    raise ValueError("Исчерпан лимит попыток авторизации")


def get_operation() -> dict[int, Callable[[float], float]]:
    return {
        1: request_money,
        2: put_money,
        3: balance,
        4: choose_card

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


def choice_operation(operation: dict[int, Callable[[float], float]], entity_type: int) -> int:
    """

    :param operation: список доступных операций
    :param entity_type: тип источник денег, 1 - банковская карта, 2 - банковский счет
    :return:
    """
    bank_account_operation = "Доступные операции:\n 1 - Снятие со счета\n 2 - Пополнение счета\n 3 - Баланс\n 0 - Вернуться в главное меню"
    card_operation = ("Доступные операции:"
                      "\n 1 - Снятие с карты"
                      "\n 2 - Пополнение карты"
                      "\n 3 - Баланс"
                      "\n 4 - Перевод на другую карту"
                      "\n 5 - Перевод на банковский счет"
                      "\n 0 - Вернуться в главное меню"
                      )
    operations = [card_operation, bank_account_operation]

    print(operations[entity_type - 1])
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


def bank_account_flow(client,
                      operation,
                      chose_operation=None,
                      input_current_bank_account=None,
                      entity_type: int = 2):
    current_bank_account = input_current_bank_account
    if current_bank_account is None:
        current_bank_account = choice_bank_account(current_bank_account, client)
    if chose_operation is None:
        client_request = choice_operation(operation, entity_type)
    else:
        client_request = chose_operation
    while client_request:
        balance = execute_operation(operation, client_request, current_bank_account)
        save(client, current_bank_account, balance)
        client_request = choice_operation(operation, entity_type)


def card_manager(client, primary_card, chose_operation, operation):
    match chose_operation:
        case 1 | 2 | 3:
            card_flow(client, primary_card, operation, chose_operation)
        case 4:
            card = choose_card(client, primary_card)
            primary_bank_account = get_card_bank_account(client, primary_card)
            card_bank_account = get_card_bank_account(client, card)
            user_request = input("Введите сумму для пополнения: ")

            while True:
                try:
                    user_request = float(user_request)
                    break
                except ValueError:
                    print("Требуется ввести число")
                if user_request <= 0:
                    print("Сумма должна быть положительной")

                if primary_bank_account["balance"] < user_request:
                    print("Не хватает средств")

                user_request = input("Введите сумму для пополнения: ")

            primary_balance = card_request_money(primary_bank_account['balance'], user_request)
            card_balance = card_put_money(card_bank_account['balance'], user_request)
            save(client, primary_bank_account, primary_balance)
            save(client, card_bank_account, card_balance)


def get_card_bank_account(client, card):
    bank_account_id = card["bank_account_id"]
    current_bank_account = None

    for bank_account in client["bank_accounts"]:
        if bank_account["id"] == bank_account_id:
            current_bank_account = bank_account
    return current_bank_account


def card_flow(client, card, operation, chose_operation):
    current_bank_account = get_card_bank_account(client, card)

    bank_account_flow(client, operation, chose_operation, current_bank_account, 1)


def choose_card(client, primary_card):
    cards = card_list(client, primary_card)
    if not cards:
        return None
    while True:
        try:
            card_id = int(input("Выберите порядковый номер карты: "))
            return cards[card_id - 1]
        except ValueError:
            print("Ошбика при вводе порядкового номера")
            continue


def card_list(client: dict[str, Any], primary_card: dict[str, str]) -> list[dict[str, str]]:
    cards = list(filter(lambda item: item != primary_card, client["cards"]))
    if not cards:
        print("Нет доступных карт")
        return []
    print("Список доступных карты: ")
    for index, card in enumerate(cards, 1):
        if primary_card['number'] != card["number"]:
            print(f"{index} - {card['number']}")
    return cards


def card_request_money(amount_money: float, input_amount: float) -> float:
    amount_money -= input_amount
    print(f"Вы сняли со счета: {input_amount:.2f}")
    print(f"Остаток по счету: {amount_money:.2f}")
    return amount_money


def card_put_money(amount_money: float, input_amount: float) -> float:
    amount_money += input_amount
    print(f"Вы пополнили счет на сумму: {input_amount:.2f}")
    print(f"Остаток по счету: {amount_money:.2f}")
    return amount_money


def main() -> None:
    try:
        client: dict[str, Any] = authorize()
        card = request_card_number(client)
    except ValueError as value_error:
        print(str(value_error))
        print("Обратитесь позже")
        return

    operation: dict[int, Callable[[float], float]] = get_operation()
    user_request = menu()
    while user_request:
        if user_request == 1:
            chose_operation = choice_operation(operation, user_request)
            card_manager(client, card, chose_operation, operation)
        elif user_request == 2:
            bank_account_flow(client, operation)

        user_request = menu()
    print("Работа завершена!")


if __name__ == '__main__':
    main()
