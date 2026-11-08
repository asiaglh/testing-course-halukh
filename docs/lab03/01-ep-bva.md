# ЛР 3. Класи еквівалентності та граничні значення — Р-08

**Тестова база:** Р-08 у специфікації лабораторної № 3. Очікування зафіксовані в `spec_cases.json` до запуску коду (коміт `693abb9`). Спільна передумова: `Grade("Python", 70, date(2026, 10, 1))`; `d = today − graded_on`. Успішне виправлення мусить залишити `course="Python"`, `graded_on=01.10.2026`, а вихідний об’єкт не змінити.

## Класи еквівалентності

| Клас | Параметр і значення | Тип | Очікування | Представник |
|---|---|---|---|---|
| S1 | Нові бали: ціле 0…100 | допустимий | оцінка з новими балами | 50 |
| S2 | Ціле < 0 | недопустимий | InvalidGradeError | −1 |
| S3 | Ціле > 100 | недопустимий | InvalidGradeError | 101 |
| S4 | Неціле дійсне число | недопустимий | InvalidGradeError | 75.5 |
| S5 | Числовий рядок | недопустимий | InvalidGradeError | "75" |
| S6 | Нечисловий рядок | недопустимий | InvalidGradeError | "abc" |
| S7 | Логічне значення (у Python є підтипом `int`) | недопустимий за вимогою «ціле число» | InvalidGradeError | True |
| S8 | Відсутнє значення | недопустимий | InvalidGradeError | None |
| D1 | d < 0 | недопустимий | CorrectionPeriodError | −1 |
| D2 | 0 ≤ d ≤ 14 | допустимий | оцінка з новими балами | 7 |
| D3 | d > 14 | недопустимий | CorrectionPeriodError | 15 |

Кожен недопустимий клас має окремий тест із допустимим другим параметром. `ТВ-EP-11` — додаткова перевірка пріоритету помилки дати, коли обидва параметри неправильні; її не використовуємо для покриття недопустимих класів.

## Граничні значення

| Межа | Значення | Аналіз | Очікуваний результат | Тести |
|---|---|---|---|---|
| бали: нижня | −1, 0 | двозначний | InvalidGradeError; оцінка 0 | ТВ-EP-02, ТВ-BVA-01 |
| бали: верхня | 100, 101 | двозначний | оцінка 100; InvalidGradeError | ТВ-BVA-02, ТВ-EP-03 |
| строк: початок | −1, 0 | двозначний | CorrectionPeriodError; оцінка 50 | ТВ-EP-09, ТВ-BVA-03 |
| строк: кінець | 14, 15 | двозначний | оцінка 50; CorrectionPeriodError | ТВ-BVA-04, ТВ-EP-10 |
| строк: кінець | 13, 14, 15, 16 | тризначний, сусідні значення з обох боків | оцінка 50; оцінка 50; CorrectionPeriodError; CorrectionPeriodError | ТВ-BVA-05, ТВ-BVA-04, ТВ-EP-10, ТВ-BVA-06 |

Дата оцінки — 01.10.2026, тому d=14 відповідає 15.10.2026. Повторно не запускали однакові пари вхідних даних: тести EP, що потрапили на межу, зараховані в BVA.

## Виконані тестові випадки

| ID | Покриває | Вхідні дані | Очікуваний результат | Фактичний результат | Статус |
|---|---|---|---|---|---|
| ТВ-EP-01 | S1, D2 | d=7, today=08.10.2026, бали=50 | `Grade` з балами 50, Python, 01.10.2026 | `Grade(course='Python', score=50, graded_on=datetime.date(2026, 10, 1))` | Пройдено |
| ТВ-EP-02 | S2, D2 | d=7, today=08.10.2026, бали=-1 | `InvalidGradeError` | `InvalidGradeError: оцінка має бути від 0 до 100, отримано -1` | Пройдено |
| ТВ-EP-03 | S3, D2 | d=7, today=08.10.2026, бали=101 | `InvalidGradeError` | `InvalidGradeError: оцінка має бути від 0 до 100, отримано 101` | Пройдено |
| ТВ-EP-04 | S4, D2 | d=7, today=08.10.2026, бали=75.5 | `InvalidGradeError` | `Grade(course='Python', score=75.5, graded_on=datetime.date(2026, 10, 1))` | **Не пройдено** |
| ТВ-EP-05 | S5, D2 | d=7, today=08.10.2026, бали='75' | `InvalidGradeError` | `TypeError: '<=' not supported between instances of 'int' and 'str'` | **Не пройдено** |
| ТВ-EP-06 | S6, D2 | d=7, today=08.10.2026, бали='abc' | `InvalidGradeError` | `TypeError: '<=' not supported between instances of 'int' and 'str'` | **Не пройдено** |
| ТВ-EP-07 | S7, D2 | d=7, today=08.10.2026, бали=True | `InvalidGradeError` | `Grade(course='Python', score=True, graded_on=datetime.date(2026, 10, 1))` | **Не пройдено** |
| ТВ-EP-08 | S8, D2 | d=7, today=08.10.2026, бали=None | `InvalidGradeError` | `TypeError: '<=' not supported between instances of 'int' and 'NoneType'` | **Не пройдено** |
| ТВ-EP-09 | S1, D1 | d=-1, today=30.09.2026, бали=50 | `CorrectionPeriodError` | `Grade(course='Python', score=50, graded_on=datetime.date(2026, 10, 1))` | **Не пройдено** |
| ТВ-EP-10 | S1, D3 | d=15, today=16.10.2026, бали=50 | `CorrectionPeriodError` | `CorrectionPeriodError: виправити оцінку можна до 15.10.2026 включно` | Пройдено |
| ТВ-EP-11 | S2, D3 | d=15, today=16.10.2026, бали=-1 | `CorrectionPeriodError` | `CorrectionPeriodError: виправити оцінку можна до 15.10.2026 включно` | Пройдено |
| ТВ-BVA-01 | S:0 | d=7, today=08.10.2026, бали=0 | `Grade` з балами 0, Python, 01.10.2026 | `Grade(course='Python', score=0, graded_on=datetime.date(2026, 10, 1))` | Пройдено |
| ТВ-BVA-02 | S:100 | d=7, today=08.10.2026, бали=100 | `Grade` з балами 100, Python, 01.10.2026 | `Grade(course='Python', score=100, graded_on=datetime.date(2026, 10, 1))` | Пройдено |
| ТВ-BVA-03 | D:0 | d=0, today=01.10.2026, бали=50 | `Grade` з балами 50, Python, 01.10.2026 | `Grade(course='Python', score=50, graded_on=datetime.date(2026, 10, 1))` | Пройдено |
| ТВ-BVA-04 | D:14 | d=14, today=15.10.2026, бали=50 | `Grade` з балами 50, Python, 01.10.2026 | `CorrectionPeriodError: виправити оцінку можна до 15.10.2026 включно` | **Не пройдено** |
| ТВ-BVA-05 | D:13 | d=13, today=14.10.2026, бали=50 | `Grade` з балами 50, Python, 01.10.2026 | `Grade(course='Python', score=50, graded_on=datetime.date(2026, 10, 1))` | Пройдено |
| ТВ-BVA-06 | D:16 | d=16, today=17.10.2026, бали=50 | `CorrectionPeriodError` | `CorrectionPeriodError: виправити оцінку можна до 15.10.2026 включно` | Пройдено |

У всіх 17 тестах вихідна `Grade` залишилася без змін. Повний машинний протокол — [`evidence/results.json`](evidence/results.json).

**Покриття:** класи еквівалентності — **11/11 (100 %)**; двозначні граничні точки — **8/8 (100 %)**; додаткові тризначні точки кінця строку — **4/4 (100 %)**. Покриття означає виконання елемента, а не проходження тесту. EP: 5/11 пройдено; BVA: 5/6 пройдено. Зокрема, на d=14 функція відхиляє допустиме виправлення, а на d=−1 приймає його.
