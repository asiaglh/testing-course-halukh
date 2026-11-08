# ЛР 5. Тестові дублери для Р-20

Галух Анна Олександрівна, 63М. Прогони виконано на app-lab05 (0.5.0), Python 3.14.10, без справжнього поштового сервера. [Протокол pytest](evidence/reminders-pytest.txt): 9 passed, 4 xfailed. Суворі `xfail` пов’язані з [#21](https://github.com/asiaglh/testing-course-halukh/issues/21), [#22](https://github.com/asiaglh/testing-course-halukh/issues/22), [#23](https://github.com/asiaglh/testing-course-halukh/issues/23).

| Тест | Залежність | Дублер | Стан чи поведінка | Чому цей вид |
|---|---|---|---|---|
| `test_fake_single_course_happy_path` | `Mailer` | `FakeMailer` | Стан `outbox`: адреса, тема, дисципліна, строк 30 днів; стан `ReminderReport` | Легко прочитати вміст листа без налаштування mock API |
| `test_fake_one_letter_lists_all_fx_courses_in_order` | `Mailer` | `FakeMailer` | Стан: рівно один лист з усіма різними Fx в алфавітному порядку | Фейк виявляє два окремі листи без реальної розсилки; xfail #22 |
| `test_autospec_eligible_student_receives_one_message` | `Mailer` | `create_autospec(Mailer, instance=True)` | Поведінка: `send` викликано один раз із правильною адресою, темою й текстом | Автоспецифікація відхиляє помилкові назви методів і дає чіткі перевірки викликів |
| `test_autospec_ineligible_student_is_not_contacted` | `Mailer` | autospec mock | Поведінка: `assert_not_called` для ON_LEAVE, EXPELLED, GRADUATED, відсутнього email і відсутнього Fx | Негативні взаємодії краще видно через mock; ON_LEAVE/GRADUATED — xfail #21 |
| `test_autospec_first_failure_does_not_stop_second_student` | `Mailer` | autospec mock із `side_effect` | Поведінка: два виклики, перша адреса в `failed`, друга в `sent` | Керований збій першого виклику перевіряє продовження без сервера; xfail #23 |
| `test_patching_smtplib_does_not_replace_imported_name` | `smtplib.SMTP` | patch у неправильному просторі імен | Поведінка: `reminders.SMTP` лишається вихідним класом | Демонструє причину помилки підміни без мережевого звернення |
| `test_smtp_uses_default_port_without_login` | `student_portal.reminders.SMTP` | `mocker.patch` | Поведінка: порт 587, STARTTLS, немає login без користувача | Підміна у просторі імен, з якого код викликає SMTP |
| `test_smtp_mailer_uses_tls_and_expected_headers` | `student_portal.reminders.SMTP` | `mocker.patch` | Поведінка: host/port, STARTTLS, login за наявності username, `send_message`, заголовки | Перевіряє протокол SMTP без реального з’єднання |

`reminders.py` виконує `from smtplib import SMTP`, тому після імпорту ім’я `SMTP` зберігається в модулі `student_portal.reminders`. `mocker.patch("smtplib.SMTP")` змінює атрибут у бібліотеці, але функція `SmtpMailer.send` звертається до **вже прив’язаного** `student_portal.reminders.SMTP`. Якби після такої помилкової підміни тест викликав `send`, він спробував би справжнє з’єднання. У тесті показано відмінність посилань, а виклик `send` зроблено лише з правильною підміною.

Відмови Р-20 належать викладацькому коду, тому його не змінено. Коли #21–23 виправлять, `xfail(strict=True)` дасть XPASS і зробить CI червоним до оновлення маркерів.
