# Универсальный чек-лист перед отправкой кода на ревью

Этот гайд — опора для большинства backend-задач: бизнес-логика, статусы, БД, транзакции, внешние сервисы, retry, JSON/payload, scheduler, UseCase/Service и тесты.

> Сначала проверь поведение системы, потом код.

Перед вопросом «правильно ли я написал код?» сначала спроси:

> **Какое состояние системы должно быть после этой ветки?**

---

## 1. Сверяю код со сценарием

Перед ревью я должен уметь ответить:

- Что запускает сценарий?
- Что приходит на вход?
- Что считается успехом?
- Какие есть альтернативные исходы?
- Что меняется?
- Что не должно меняться?

Пример:

```text
EVENT:
Scheduler запустил обработку сообщения.

INPUT:
OutboxMessage.

SUCCESS:
Сообщение отправлено.

POSTCONDITIONS:
OutboxMessage.status = SENT
Subscription.last_notified_at != None
```

Если это нельзя объяснить словами — код ещё рано ревьюить.

---

## 2. Проверяю ответственность класса / функции

Вопрос:

> **Какую одну операцию делает этот класс?**

Хорошо:

```text
CheckProductPriceUseCase
→ проверяет цену одного товара

SendNotificationUseCase
→ обрабатывает отправку одного уведомления

EmailSender
→ делает одну физическую попытку отправки email
```

Если для описания класса нужно 4–5 глаголов, возможно, ответственности смешаны.

---

## 3. Определяю единицу работы

Спрашиваю:

> **Что обрабатывает один вызов `execute()`?**

Например:

```text
один Product
одну Subscription
один OutboxMessage
один Order
```

Часто:

```text
Selector
→ получает много объектов

Orchestrator / Command
→ перебирает их

UseCase
→ обрабатывает один объект
```

---

## 4. Проверяю Preconditions

Preconditions — что должно быть правдой ДО выполнения действия.

Пример:

```text
Product approved
Product active
Subscription active
price is not None
price <= desired_price
```

Полезный вопрос:

> Если условие не выполнено, это ошибка или нормальный бизнес-исход?

Например:

```text
Subscription inactive
→ возможно CANCELLED

сломанный payload
→ возможно FAILED

SMTP timeout
→ retry
```

---

## 5. Проверяю Postconditions

Postconditions — что должно быть гарантировано ПОСЛЕ выполнения.

Пример успеха:

```text
status = SENT
error_message = None
last_notified_at заполнен
```

Пример временной ошибки:

```text
retry_count увеличен
status остаётся PENDING
```

---

## 6. Проверяю Invariants

Инвариант — правило, которое система не должна нарушать вообще.

Примеры:

```text
У одной Subscription не может быть двух PENDING сообщений.

SENT нельзя снова отправлять.

FAILED — финальное состояние.

Цена подписки должна быть > 0.
```

Если правило критичное, подумай, нужно ли защищать его БД:

```text
UniqueConstraint
CheckConstraint
NOT NULL
ForeignKey
```

---

## 7. Если есть status — рисую State Machine

Минимум:

```text
PENDING
├── success → SENT
├── irrelevant → CANCELLED
└── too many errors → FAILED
```

Потом проверяю запрещённые переходы:

```text
SENT → FAILED ?
SENT → CANCELLED ?
FAILED → SENT ?
CANCELLED → PENDING ?
```

Если код допускает переход, которого нет в схеме, нужно остановиться.

---

## 8. После финального состояния проверяю `return`

Частая ошибка:

```text
PENDING
→ CANCELLED
→ код продолжил работу
→ send()
```

Поэтому после каждой ветки спрашиваю:

> **Должно ли выполнение продолжаться?**

Пример:

```python
if business_invalid:
    mark_cancelled()
    return
```

---

## 9. Перед `.update()` проверяю модель

Перед:

```python
SomeModel.objects.filter(...).update(...)
```

проверяю:

1. Какую модель я обновляю?
2. Какой объект этой модели я хочу изменить?
3. Есть ли у неё эти поля?

Пример:

```python
OutboxMessage.objects.filter(pk=outbox_message.pk)
```

а не:

```python
OutboxMessage.objects.filter(pk=subscription.pk)
```

Мнемоника:

```text
Model.objects
→ pk должен принадлежать объекту этой Model
```

---

## 10. Проверяю принадлежность полей

Перед:

```python
.update(status=..., last_notified_at=...)
```

спрашиваю:

> **Какой сущности принадлежит каждое поле?**

Пример:

```text
OutboxMessage:
- status
- retry_count
- error_message
- payload

Subscription:
- desired_price
- is_active
- last_notified_at
```

---

## 11. После QuerySet `.update()` помню про старый Python-объект

Например:

```python
Model.objects.filter(pk=obj.pk).update(
    retry_count=F("retry_count") + 1
)
```

БД уже изменилась, но:

```python
obj.retry_count
```

может быть старым.

Если новое значение нужно дальше:

```python
obj.refresh_from_db()
```

Мнемоника:

```text
.update()
→ обновил БД

refresh_from_db()
→ обновил объект в памяти
```

---

## 12. Прогоняю счётчики вручную

Если есть:

```text
retry_count
attempts
consecutive_errors
limit
```

рисую:

```text
0
↓ ошибка
1
↓ ошибка
2
↓ ошибка
3 → FAILED
```

Проверяю:

```text
когда увеличивается счётчик?
до проверки?
после проверки?
что происходит ровно на границе?
```

Это помогает ловить off-by-one ошибки.

---

## 13. Проверяю boolean-условия словами

Перед:

```python
if something:
```

перевожу условие на русский.

Плохой пример:

```python
if payload.get("email"):
    raise ValueError("Email отсутствует")
```

Перевод:

```text
Если email существует
→ сказать, что email отсутствует.
```

Особенно внимательно:

```text
if / not
is None / is not None
> / >=
< / <=
```

---

## 14. Проверяю граничные значения

Если правило:

```text
price <= desired_price
```

проверяю:

```text
80 < 100
100 == 100
120 > 100
```

Если лимит:

```text
MAX_ATTEMPTS = 3
```

проверяю:

```text
2
3
4
```

Если данные могут быть пустыми:

```text
None
""
{}
[]
0
```

---

## 15. Проверяю структуру данных, а не только `None`

Плохо:

```python
if payload is not None:
    ...
```

Потому что возможны:

```python
{}
{"email": ""}
{"message": None}
[]
"hello"
```

Правильный вопрос:

> **Соответствуют ли данные ожидаемому контракту?**

Например:

```text
payload должен быть dict
email должен быть непустым
message должен быть непустым
```

---

## 16. Разделяю типы ошибок

Полезно различать минимум три категории.

### Бизнес-условие

Пример:

```text
пользователь отменил подписку
```

Результат:

```text
CANCELLED
```

### Технически сломанные данные

Пример:

```text
payload не содержит email
```

Результат:

```text
FAILED
```

Повтор обычно не поможет.

### Временная внешняя ошибка

Пример:

```text
SMTP timeout
HTTP 503
```

Результат:

```text
retry_count + 1
PENDING / FAILED после лимита
```

---

## 17. Перед `raise` спрашиваю: кому нужен exception?

Вопрос:

> **Кто поймает это исключение и что сделает дальше?**

Если ответа нет, exception может быть лишним.

Например:

```text
Business invalid
→ CANCELLED
→ return
```

может быть лучше, чем:

```text
CANCELLED
→ raise
```

если это ожидаемый исход.

---

## 18. Внешний side effect отделяю от транзакции БД

Внешние действия:

```text
email
HTTP
push
файлы
внешний API
```

нельзя откатить через:

```python
transaction.atomic()
```

Пример:

```text
email отправился
↓
DB rollback
```

Email уже не исчезнет.

Поэтому спрашиваю:

> **Что именно я хочу сделать атомарным?**

Хорошо:

```text
send email

после успеха:

transaction.atomic():
    Outbox → SENT
    Subscription → notified
```

---

## 19. Не храню временные данные `execute()` в `self`

Проверяю:

```python
self.something = ...
```

Вопрос:

> Это зависимость класса или данные одного вызова?

Хорошо:

```python
self.sender = sender
```

Сомнительно:

```python
self.subscription = subscription
```

если нужна только внутри одного `execute()`.

---

## 20. Проверяю копипасту

Перед ревью ищу:

```text
повтор метода
не тот pk
не та модель
не тот exception
не то имя переменной
```

Пример:

```python
self._state_check(...)
...
self._state_check(...)
```

хотя второй вызов должен быть:

```python
self._tech_condition(...)
```

---

## 21. Прогоняю код вручную минимум по 5 сценариям

### 1. Happy path

```text
всё валидно
→ успех
```

### 2. Business failure

```text
объект больше не подходит
→ CANCELLED / stop
```

### 3. Technical failure

```text
данные сломаны
→ FAILED
```

### 4. Temporary external failure

```text
SMTP / HTTP упал
→ retry
```

### 5. Boundary case

```text
последняя попытка
равенство цены
пустое значение
повторный запуск
```

Если я не могу вручную объяснить путь по коду — код ещё стоит перечитать.

---

## 22. Проверяю повторный запуск

Спрашиваю:

> **Что будет, если `execute()` вызовут второй раз?**

Например:

```text
SENT
→ execute()
→ send повторно?
```

Если да, это может быть баг.

Важно различать:

```text
повторный последовательный вызов

и

два конкурентных процесса
```

---

## 23. Проверяю concurrency отдельно

Спрашиваю:

> **Что если два процесса делают это одновременно?**

Пример:

```text
Process A: видит PENDING
Process B: видит PENDING

оба отправляют email
```

Возможные инструменты:

```text
UniqueConstraint
select_for_update
atomic update
claim status
F()
```

Но сначала нужно понять конкретную гонку.

---

## 24. Не надеюсь, что `transaction.atomic()` решит все гонки

Помню:

```text
transaction.atomic
→ commit / rollback группы DB-операций

UniqueConstraint
→ защита инварианта

select_for_update
→ блокировка существующей строки

F()
→ атомарное относительное обновление
```

Это разные инструменты.

---

## 25. Проверяю QuerySet на N+1

Если в цикле:

```python
for subscription in subscriptions:
    subscription.product
    subscription.user
```

спрашиваю:

> Не будет ли отдельного SQL-запроса на каждый объект?

Для ForeignKey часто помогает:

```python
select_related("product", "user")
```

---

## 26. Проверяю, не делаю ли лишний запрос

Например:

```python
if queryset.exists():
    obj = queryset.get(...)
```

Иногда достаточно сразу:

```python
obj = queryset.get(...)
```

Также:

```python
for obj in queryset:
```

не требует предварительного:

```python
queryset.count()
```

---

## 27. Проверяю ORM-метод по смыслу задачи

Памятка:

```text
найти
→ get / filter

найти или создать
→ get_or_create

найти и обновить, либо создать
→ update_or_create

относительно изменить число
→ F()

объединить DB-изменения
→ transaction.atomic

заблокировать существующую строку
→ select_for_update

загрузить FK сразу
→ select_related
```

Инструмент выбирается после понимания поведения.

---

## 28. Перед тестами выписываю Given / When / Then

Пример:

```text
Given:
PENDING message
retry_count = 0
valid payload

When:
sender successfully sends

Then:
status = SENT
last_notified_at is set
sender.send called once
```

---

## 29. В тестах различаю State и Interaction verification

### State verification

Что стало с системой:

```python
self.assertEqual(outbox.status, SENT)
self.assertIsNotNone(subscription.last_notified_at)
```

### Interaction verification

С кем взаимодействовал код:

```python
sender.send.assert_called_once_with(...)
```

---

## 30. После выполнения UseCase обновляю объекты из БД

Если production-код использует:

```text
.update()
F()
save()
```

перед assertion:

```python
obj.refresh_from_db()
```

И только потом проверяю состояние.

---

## 31. Проверяю точность assertions

Слабая проверка:

```python
self.assertNotEqual(old_payload, new_payload)
```

Она говорит только:

```text
что-то изменилось
```

Сильнее:

```python
self.assertEqual(
    new_payload["message"],
    expected_message,
)
```

Проверяй конкретный бизнес-результат.

---

## 32. Не парсю собственный output без необходимости

Если ожидаемое значение известно:

```python
expected_message = "..."
```

лучше:

```python
self.assertEqual(actual, expected_message)
```

чем разбирать строку обратно через `split`, `index` и т. п.

Тест должен быть проще production-кода.

---

## 33. Проверяю названия

Название должно отражать поведение.

Хорошо:

```python
test_updates_pending_payload_when_desired_price_changes
```

Слабее:

```python
test_change_price
```

Для методов тоже проверяю:

> Понятно ли по названию, что именно делает метод?

---

## 34. Проверяю magic strings и magic numbers

Плохо:

```python
status="PENDING"
if retry_count >= 3:
```

Лучше:

```python
status=OutboxMessage.State.PENDING

MAX_ATTEMPTS = 3
```

---

## 35. Проверяю `save()`

Если меняется одно поле:

```python
obj.status = ...
obj.save(update_fields=["status"])
```

Это точнее, чем:

```python
obj.save()
```

---

## 36. Проверяю внешние зависимости

Если UseCase зависит от внешней системы:

```text
SMTP
HTTP
payment API
storage
```

лучше передавать зависимость:

```python
UseCase(sender)
```

чем создавать её глубоко внутри метода.

Это упрощает тестирование и замену реализации.

---

## 37. Последняя проверка: могу ли я объяснить каждую важную строку?

Например:

```python
obj.refresh_from_db()
```

Ответ:

```text
До этого был QuerySet.update(),
поэтому Python-объект содержит старое значение.
```

Или:

```python
with transaction.atomic():
```

Ответ:

```text
Эти два изменения БД должны сохраниться вместе.
```

Если ответ:

```text
"ну вроде так надо"
```

значит место нужно ещё понять.

---

# Короткий чек-лист на 2 минуты

```text
□ Я могу описать сценарий без кода?

□ Понятно, что получает execute()?

□ У класса одна основная ответственность?

□ Preconditions понятны?

□ Postconditions понятны?

□ Я знаю инварианты?

□ State Machine выписана?

□ Нет запрещённых переходов состояний?

□ После финальной ветки стоит return, если он нужен?

□ В каждом QuerySet правильная модель?

□ Используется pk правильной сущности?

□ Поля принадлежат той модели, которую обновляю?

□ После .update() не читаю старый Python-объект?

□ Если читаю — сделал refresh_from_db()?

□ Счётчик прогнан вручную 0 → 1 → 2 → ...?

□ Нет off-by-one на лимите?

□ Я перевёл все if-условия на человеческий язык?

□ Проверены <, ==, >?

□ Проверены None / "" / {}?

□ JSON/payload соответствует контракту?

□ Я различаю business / technical / temporary errors?

□ Каждый raise кому-то реально нужен?

□ Внешний side effect не считается откатываемым транзакцией?

□ В self нет временного состояния одного execute()?

□ Нет копипастной ошибки?

□ Повторный execute() не ломает состояние?

□ Я подумал о двух одновременных процессах?

□ Нет N+1?

□ Нет очевидно лишних запросов?

□ ORM-метод соответствует смыслу задачи?

□ Есть Given / When / Then?

□ Тесты проверяют state?

□ Тесты проверяют interaction, где нужно?

□ Assertions проверяют конкретный результат?

□ Названия методов и тестов отражают поведение?

□ Magic strings/numbers вынесены?

□ Я могу объяснить каждую важную строку?
```

---

# Универсальный шаблон перед новой задачей

```markdown
# Название сценария

## Цель

Что должна сделать система?

## Event

Что запускает сценарий?

## Input

Что приходит на вход?

## Preconditions

- 
- 
- 

## Postconditions

После успеха:

- 
- 
- 

После ошибки:

- 
- 
- 

## Invariants

- 
- 
- 

## States

STATE_A
STATE_B
STATE_C

## State transitions

| Было | Событие | Стало |
|---|---|---|
| | | |

## Decision table

| Условие | Результат |
|---|---|
| | |

## Boundary cases

- меньше;
- равно;
- больше;
- None;
- пусто;
- повторный запуск;
- последняя попытка.

## Concurrency

Что если два процесса выполнят это одновременно?

## External side effects

Есть ли SMTP / HTTP / файлы / внешнее API?

Можно ли их откатить?

## Transaction boundary

Какие DB-изменения должны коммититься вместе?

## Given / When / Then

### Case 1

Given:

When:

Then:

### Case 2

Given:

When:

Then:
```

---

# Главное правило

Когда код становится запутанным, не добавляй ещё один `if`.

Вернись к цепочке:

```text
сценарий
↓
условия
↓
состояния
↓
переходы
↓
граничные случаи
↓
ошибки
↓
тесты
↓
код
```

Код должен быть реализацией уже понятного поведения, а не местом, где это поведение придумывается.
