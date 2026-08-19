amount_money = 1000.00


def request_money(amount_money) -> float:
    while True:
        user_request = input("Введите сумму для снятия: ")
        try:
            user_request = float(user_request)

        except ValueError:
            print("Требуется ввести число")
            continue

        if user_request < 0:
            print("Сумма должна быть положительной")

        elif user_request > amount_money:
            print("Недостаточно средств")
        else:
            return user_request


user_request = request_money(amount_money)
amount_money -= user_request

print(f"Вы сняли: {user_request: .2f}")
print(f"Остаток по счету: {amount_money: .2f}")
