# ЛР 7 — перевірка OpenAPI інструментом Schemathesis

**Галух Анна Олександрівна, 63М.** Версія API `app-lab07` (0.7.0), Schemathesis 4.33.1, seed `20261108`, по 50 прикладів на операцію. Сервер запущено окремо на копії `data/group.json`; обидві ролі перевірялися на свіжих даних.

```sh
cd app
uv run student-portal-api
uv run schemathesis run http://127.0.0.1:8000/openapi.json -H 'Authorization: Bearer admin-token' --max-examples 50 --seed 20261108
uv run schemathesis run http://127.0.0.1:8000/openapi.json -H 'Authorization: Bearer teacher-token' --max-examples 50 --seed 20261108
```

Локально використовувався порт 8765 замість 8000; він не впливає на результат. Для адміністратора згенеровано **414** випадків, 7/7 операцій перевірено, 4 унікальні відмови та одне попередження. Для викладача — **643** випадки, 7/7 операцій, ті самі 4 унікальні відмови та одне попередження. Фаза stateful завершилася, coverage і fuzzing показали відмови; examples були пропущені.

| Код | Запит | Спостереження | Класифікація | Дія |
| --- | --- | --- | --- | --- |
| ST103 | `POST /api/students` | Пошкоджений JSON дає 400; схема описує 201, 401, 403, 409, 422 | Невідповідність OpenAPI фактичній відповіді FastAPI на некоректне тіло | [#38](https://github.com/asiaglh/testing-course-halukh/issues/38), тест `test_openapi.py` |
| ST103 | `POST /api/grades` | Пошкоджений JSON дає 400; схема описує 201, 401, 403, 404, 409, 422 | Та сама невідповідність на другому POST | [#38](https://github.com/asiaglh/testing-course-halukh/issues/38), тест `test_openapi.py` |
| ST205 | `OPTIONS /api/students` | 405 із `Allow: GET`; у схемі також POST | Особливість автоматичної відповіді маршрутизатора FastAPI/Starlette на OPTIONS; самі GET і POST доступні | Зафіксовано як обмеження фреймворкової відповіді; якщо OPTIONS стане частиною публічного контракту, виправити заголовок |
| ST205 | `OPTIONS /api/students/{id}` | 405 із `Allow: GET`; у схемі також PUT і DELETE | Та сама особливість маршрутизатора | Та сама дія |

Попередження про 401/403 пов'язані з налаштуванням одного токена на всі операції: `admin-token` не може `POST /api/grades`, а `teacher-token` не може `POST /api/students` і `DELETE /api/students/{id}`. Це очікуване розмежування ролей за Р-23, не дефекти авторизації. Schemathesis повідомляє про операції, для яких ця роль не отримала успішної відповіді.

Окреме статичне порівняння `/openapi.json` з Р-23 виявило, що `GradeIn.score` має `minimum: 1` замість **0** ([#33](https://github.com/asiaglh/testing-course-halukh/issues/33)), а `StudentOut` не містить `funding`, потрібного клієнту деканату за Р-24 ([#37](https://github.com/asiaglh/testing-course-halukh/issues/37)). Граничний тест Р-23 і Pact підтверджують ці розбіжності. Schemathesis генерує запити з OpenAPI, а OpenAPI тут створено з тих самих моделей, що й сервер: тому 0 балів він вважає невалідними за схемою і не знаходить суперечності з Р-23. Для цього потрібен незалежний оракул вимог — тести `test_grades_api.py` та контракт споживача.
