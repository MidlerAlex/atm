import json
from typing import Callable


def create_json(file_name: str, data: dict[str, float]) -> None:
    with open(file_name, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def request_pin_code() -> None:
    pin_code = input("Введите ваш пин-код: ")
    if pin_code.isdigit() and len(pin_code) == 4:
        return
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
    amount_money: float = 0.0

    with open("balance.json", "r") as file:
        balance_json = json.load(file)
        amount_money = balance_json["amount_money"]

    while True:
        if not is_authorized:
            try:
                request_pin_code()
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

        with open("balance.json", "w") as file:
            balance_dict = {
                "amount_money": amount_money,
            }
            json.dump(balance_dict, file, indent=4)


if __name__ == '__main__':
    # data = {
    #     "amount_money": 1000,
    # }
    # file_name = 'balance.json'
    # create_json(file_name, data)
    main()
