amount_money = 1000.00

user_request = float(input("Введите сумму для снятия: "))

amount_money -= user_request

print(f"Вы сняли: {user_request: .2f}")
print(f"Остаток по счету: {amount_money: .2f}")
