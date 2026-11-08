# ЛР 7 — автоматизовані тести REST API

**Галух Анна Олександрівна, 63М.** Об'єкт: `student-portal` 0.7.0 (`app-lab07`). Джерело очікувань — незалежна специфікація Р-23, а не OpenAPI, згенерована з реалізації. Тести запускають справжній HTTP-сервер на випадковому локальному порту та копію `data/group.json`; оригінальні дані не змінюються. Кожен тест запису створює студента з унікальним email.

| Запит Р-23 | Що перевірено | Тести | Результат |
| --- | --- | --- | --- |
| `GET /api/students` | 200, точна схема кожного студента, середній бал Коваль Олени 92,5; фільтр групи й порожній список | `test_students_api.py::test_list_and_get_student_match_schema_and_known_average`, `test_group_filter_returns_matching_and_empty_classes` | пройдено |
| `POST /api/students` | 201, `Location`, читання назад, `average=null`, зайві поля; межі імені та прізвища 0/1/50/51; некоректний email, `null`, відсутні поля; email без урахування регістру | `test_students_api.py::test_create_round_trip_location_and_null_average`, `test_name_length_boundaries`, `test_required_fields_reject_null_and_absence`, `test_invalid_email_is_rejected`, `test_create_rejects_email_duplicate_ignoring_case` | пройдено |
| `GET /api/students/{id}` | 200, точна схема, 404 для відсутнього; власний/чужий об'єкт | `test_students_api.py::test_list_and_get_student_match_schema_and_known_average`, `test_unknown_student_is_404`, `test_access.py` | пройдено |
| `PUT /api/students/{id}` | 200 і наступний GET, свій email; невалідні тіла без зміни даних; дублікат email; 404; право ролі | `test_students_api.py::test_update_round_trip_and_keep_own_email`, `test_update_rejects_invalid_body_without_changing_student`, `test_update_rejects_another_students_email_ignoring_case`, `test_unknown_student_is_404`, `test_access.py` | дублікат email: [#31](https://github.com/asiaglh/testing-course-halukh/issues/31); право викладача: [#34](https://github.com/asiaglh/testing-course-halukh/issues/34) |
| `DELETE /api/students/{id}` | 204 без тіла, потім 404; неіснуючий id; ролі | `test_students_api.py::test_delete_returns_no_body_then_get_is_404`, `test_unknown_student_is_404`, `test_access.py` | неіснуючий id: [#32](https://github.com/asiaglh/testing-course-halukh/issues/32) |
| `POST /api/grades` | −1/0/1/100/101, межі ECTS 59/60, 66/67, 74/75, 81/82, 89/90; назва дисципліни 0/1/100/101, дробове число, `null`, відсутні поля; 404 | `test_grades_api.py::test_score_and_ects_boundaries`, `test_invalid_grade_classes_are_422`, `test_course_name_valid_boundaries`, `test_grade_for_unknown_student_is_404` | 0 балів: [#33](https://github.com/asiaglh/testing-course-halukh/issues/33) |
| `GET /api/students/{id}/grades` | 200, точна схема, дата, порядок за датою, дві нові оцінки та змінене середнє; власні/чужі оцінки | `test_grades_api.py::test_seed_grades_are_sorted_by_date`, `test_two_grades_update_average_and_are_listed_in_date_order`, `test_access.py` | чужі оцінки: [#35](https://github.com/asiaglh/testing-course-halukh/issues/35) |

Схеми відповідей у `tests/lab07/schemas.py` вимагають **рівно** поля Р-23 (`additionalProperties: false`) і перевіряють типи, межі, email та дату. Тому додавання `funding` у відповідь для Р-24 без узгодження контракту порушило б Р-23.

## Матриця доступу

Коди — очікування Р-23. Тест `test_access.py::test_role_operation_matrix` виконує всі 54 комірки. `GET` для студентів 1 і 2 та їхніх оцінок винесено окремо, щоб перевірити BOLA. `PUT` і `DELETE` націлені на створеного в тесті студента.

| Роль / токен | Список | POST студент | GET 1 | GET 2 | PUT | DELETE | POST оцінка | Оцінки 1 | Оцінки 2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Без токена | 401 | 401 | 401 | 401 | 401 | 401 | 401 | 401 | 401 |
| Невідомий токен | 401 | 401 | 401 | 401 | 401 | 401 | 401 | 401 | 401 |
| Адміністратор | 200 | 201 | 200 | 200 | 200 | 204 | 403 | 200 | 200 |
| Викладач | 200 | 403 | 200 | 200 | 403 | 403 | 201 | 200 | 200 |
| Студент 1 | 403 | 403 | 200 | 403 | 403 | 403 | 403 | 200 | 403 |
| Студент 2 | 403 | 403 | 403 | 200 | 403 | 403 | 403 | 403 | 200 |

Кожна роль, включно з адміністратором, отримує лише права, перелічені у Р-23: `POST /api/grades` належить викладачу. Окремі тести перевіряють порядок 401 → 403 → 404 → 409/422, зокрема чужий неіснуючий id. Для викладацького PUT, чужих оцінок і голого токена є відтворювані дефекти [#34](https://github.com/asiaglh/testing-course-halukh/issues/34), [#35](https://github.com/asiaglh/testing-course-halukh/issues/35), [#39](https://github.com/asiaglh/testing-course-halukh/issues/39). Тести позначені `xfail(strict=True)`: після виправлення дефекту несподіваний успіх зламає CI, доки очікування не оновлять.

## Запуск і межі перевірки

```sh
cd app
uv run pytest -q tests/lab07
uv run pytest --cov --cov-report=term-missing
```

Локально: **121 пройдено, 13 очікуваних відмов** у ЛР 7; увесь набір: **225 пройдено, 35 очікуваних відмов**, загальне покриття з гілками **93,19%** (поріг 85%). Числа стосуються `app-lab07` і поточних тестів, а не усунення дефектів. Обмеження: вбудовані фіксовані токени та відсутність реального зовнішнього сервісу роблять ці перевірки навчальними; Pact перевіряє саме узгодження API з клієнтом деканату.
