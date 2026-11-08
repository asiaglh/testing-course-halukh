# ЛР 6. Інтеграційні тести PostgreSQL

**Галух Анна Олександрівна, 63М.** Вимога Р-22; версія `app-lab06` 0.6.0. Тести: [`conftest.py`](../../app/tests/lab06/conftest.py), [`test_repository_pg.py`](../../app/tests/lab06/test_repository_pg.py), [`test_repository_properties.py`](../../app/tests/lab06/test_repository_properties.py). Справжній PostgreSQL 18 запускається через Testcontainers один раз на сесію, щоб не витрачати час на старт контейнера для кожного тесту. Кожен тест відкриває окреме з'єднання й зовнішню транзакцію з `force_rollback=True`, тож дані одного тесту не впливають на інший. Кожен приклад Hypothesis має додатковий вкладений відкат; саме тому можна обґрунтовано вимкнути `HealthCheck.function_scoped_fixture` для цієї властивості.

| Пункт Р-22 / клас даних | Тест | Факт | Issue | Чи допоміг би фейк БД? |
| --- | --- | --- | --- | --- |
| Схема, повторне створення | `test_schema_creation_is_idempotent` | пройшов | — | Фейк не перевіряє SQL DDL та реальну ідемпотентність таблиць. |
| Повне збереження полів, email, форма, статус, оцінки | `test_add_get_round_trip_all_fields` | пройшов | — | Модель у пам'яті перевірила б контракт, але не типи й серіалізацію PostgreSQL. |
| Повторний `id`, помилка домену, незмінність даних, працездатність з'єднання | `test_duplicate_id_has_domain_error_and_leaves_connection_usable` | `xfail(strict=True)`: `UniqueViolation`, транзакція в стані `INERROR` | [#26](https://github.com/asiaglh/testing-course-halukh/issues/26) | Список міг би показати дубль, але не стан з'єднання після SQL-помилки. |
| Порядок оцінок за датою | `test_get_returns_grades_ordered_by_date` | пройшов | — | Фейк міг би перевірити логіку сортування, але не SQL `ORDER BY`. |
| Неіснуючий студент у `get` | `test_get_unknown_student_raises_domain_error` | пройшов | — | Так, якщо фейк реалізує той самий контракт. |
| `add_grade`: наявний / відсутній студент | `test_add_grade_to_existing_student`, `test_add_grade_to_unknown_student_leaves_connection_usable` | пройшли | — | Фейк перевірив би виняток, але не зовнішній ключ та savepoint. |
| Пошук: пробіли, порожній запит | `test_find_trims_whitespace_and_empty_query_returns_everyone` | пройшов | — | Так, якщо фейк моделює обрізання й порожній запит. |
| Пошук кирилицею в іншому регістрі | `test_find_ignores_case_of_cyrillic` | `xfail(strict=True)`: порожній результат | [#27](https://github.com/asiaglh/testing-course-halukh/issues/27) | Python-фейк з `casefold()` пройшов би й приховав помилку SQL `LIKE`. |
| Буквальні `%` і `_` | `test_find_treats_sql_wildcards_as_literal_characters` | обидва `xfail(strict=True)`: зайвий збіг | [#28](https://github.com/asiaglh/testing-course-halukh/issues/28) | Фейк зі звичайним `in` не відтворив би семантику шаблонів SQL. |
| Однакові прізвища, порядок за ім'ям | `test_find_sorts_same_last_name_by_first_name` | пройшов | — | Так, якщо фейк явно сортує за двома полями. |
| Літери Ґ, Є, І, Ї в українському порядку | `test_find_uses_ukrainian_alphabet_order` | `xfail(strict=True)`: Ґ у кінці | [#29](https://github.com/asiaglh/testing-course-halukh/issues/29) | Фейк з Python-сортуванням теж не гарантує українського порядку; правильний фейк міг би приховати колацію PostgreSQL. |
| Довільний студент: `get(add(student)) == student` | `test_student_survives_postgres_round_trip` | пройшов, 60 прикладів | — | Фейк перевірив би лише модель, не справжнє збереження. |

Стратегія round-trip використовує `st.builds(Student, ...)`: `id=1`, непорожні українські імена з обмеженої множини, email `None` або `student@example.edu`, усі `Funding` і `Status`, 0–5 оцінок з балами 0–100 та датами 2025–2026. Оцінки впорядковано за датою ще до збереження, бо Р-22 гарантує рівність лише для такого вхідного списку. Стратегія не генерує довільний Unicode або дуже довгі рядки; результат не доводить, що такі дані підтримані. Даних, які PostgreSQL відхилив поза специфікацією, у цьому прогоні не було.

**Локальний результат:** [протокол повного набору](evidence/pytest-full-local.txt) — 98 passed, 22 xfailed, загальне покриття з гілками 89,73% при порозі 85%; `retake.py` повністю покритий. Для запуску: `cd app && uv run pytest --cov --cov-report=term-missing`; потрібен запущений Docker. У CI завдання `tests` використовує Docker на `ubuntu-latest` і запускає весь каталог `app/tests/`, включно з ЛР 6.
