# ЛР 8 — сценарії E2E за Р-25

**Галух Анна Олександрівна, 63М.** Версія `app-lab08` (0.8.0). Тести `app/tests/lab08/test_ui.py` працюють у headless Chromium зі справжнім HTTP-сервером на копії `data/group.json`. Кожен тест отримує новий контекст браузера; записи для змін створюються з унікальним email, початкових студентів не видаляють. Класи `LoginPage`, `StudentsPage`, `StudentCard` містять локатори й дії, а очікування результатів — у тестах.

## Короткий ручний огляд

8 листопада 2026 року відкрито `/` у Chrome на локальному сервері з копією початкових даних. Після входу адміністратор бачить список із п'яти студентів, форму додавання й кнопки видалення; у списку середній бал Коваль Олени показаний як `93`. Викладач бачить список без адміністративних дій, а в картці Коваль Олени — форму нової оцінки та `92,5`. Студент 1 потрапляє відразу на власну картку без списку й форми оцінки. Ці спостереження перевірено нижче автоматизованими сценаріями.

| Правило Р-25 | Роль | Тест | Результат |
| --- | --- | --- | --- |
| Невідомий токен → `alert`, форма лишається | гість | `test_unknown_token_keeps_login_and_shows_alert` | пройдено |
| Вхід, назва ролі та вихід до форми | адміністратор, викладач | `test_staff_login_role_and_logout` | 2 пройдено |
| Лише власна картка, без переходу до списку й форми оцінки; вихід | студент 1, студент 2 | `test_student_sees_only_own_card_without_staff_controls` | 2 пройдено |
| Заголовок, стовпці, email, безоцінковий `-`, лічильник, адміністративні дії | адміністратор | `test_admin_list_columns_values_and_actions` | пройдено |
| Один знак після коми в списку: `92,5`, `82,0` | адміністратор | `test_list_average_has_one_decimal` | [#41](https://github.com/asiaglh/testing-course-halukh/issues/41), 2 `xfail` |
| Викладач бачить картки й форму оцінки, але не додавання/видалення | викладач | `test_teacher_can_view_cards_but_not_admin_actions` | пройдено |
| Пошук за частиною прізвища, порожній результат | адміністратор | `test_search_by_partial_surname_and_empty_result` | пройдено |
| Пошук без урахування регістру | адміністратор | `test_search_ignores_case` | [#42](https://github.com/asiaglh/testing-course-halukh/issues/42), `xfail` |
| Додавання: новий рядок, `status`, очищення форми й збільшення «Усього» | адміністратор | `test_add_success_updates_row_total_message_and_clears_form` | пройдено |
| Повторний email (без урахування регістру) → повідомлення й незмінна таблиця; поля лишаються | адміністратор | `test_duplicate_email_shows_error_and_keeps_table`, `test_duplicate_email_keeps_input_for_correction` | повідомлення пройдено; збереження полів — [#43](https://github.com/asiaglh/testing-course-halukh/issues/43), `xfail` |
| Інша помилка даних (51 символ) → повідомлення й незмінна таблиця; поля лишаються | адміністратор | `test_invalid_student_data_shows_error_and_keeps_table`, `test_invalid_student_data_keeps_input_for_correction` | повідомлення пройдено; збереження полів — [#43](https://github.com/asiaglh/testing-course-halukh/issues/43), `xfail` |
| Підтвердження видалення: діалог, зникнення рядка, `status`, зменшення «Усього» | адміністратор | `test_delete_confirm_removes_row_and_shows_message`, `test_delete_confirm_decrements_total` | дія пройдена; лічильник — [#45](https://github.com/asiaglh/testing-course-halukh/issues/45), `xfail` |
| Скасування видалення не надсилає DELETE | адміністратор | `test_delete_cancel_sends_no_delete_request` | [#44](https://github.com/asiaglh/testing-course-halukh/issues/44), `xfail` |
| Картка: ім'я, середній бал, оцінки/ECTS/дата, повернення до списку | адміністратор | `test_card_shows_grades_average_and_returns_to_list` | пройдено |
| Нова оцінка: рядок, ECTS, дата, середній бал, `status`, очищення форми | викладач | `test_teacher_adds_grade_to_own_test_student` | пройдено |
| Список після повернення показує актуальний середній бал | викладач | `test_back_to_list_shows_current_average` | [#46](https://github.com/asiaglh/testing-course-halukh/issues/46), `xfail` |
| Бали поза 0–100 → `alert`; 0 балів допустимі | викладач | `test_grade_outside_range_shows_error`, `test_zero_grade_is_valid` | −1/101 пройдено; 0 — відомий дефект API [#33](https://github.com/asiaglh/testing-course-halukh/issues/33), `xfail` |

Усі перевірки стану сторінки виконано через `expect(locator)`, який повторює перевірку до потрібного стану. Виняток — демонстраційний наївний тест у `test_flaky.py`; там навмисно використано миттєвий `text_content()`. Під час скасування видалення додатково перевіряється подія мережевого запиту, бо одна лише перевірка видимого рядка могла б пройти до завершення асинхронного видалення. Тестований продукт має попередні відомі дефекти Р-23; жоден `xfail` не позначає тест як виправлення продукту.

Локальний результат `test_ui.py` без затримки: **16 passed, 9 xfailed**. Відомі дефекти позначено `xfail(strict=True, raises=AssertionError)`: після виправлення продукту XPASS вимагатиме оновлення тесту та issue.
