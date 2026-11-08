# ЛР 5. Автоматизація випадків ЛР 3

Галух Анна Олександрівна, 63М. Джерело входів та очікувань — `docs/lab03/spec_cases.json`, зафіксований до прогону ЛР 3. Тести лежать у `app/tests/lab05/test_lab03_cases.py`; жодне очікування не змінено під фактичну поведінку 0.5.0. `xfail(strict=True)` містить номер issue. Для ТВ-DT-19 це [питання #18](https://github.com/asiaglh/testing-course-halukh/issues/18), а не підтверджений дефект реалізації.

Запуск на app-lab05: **55 випадків, 43 passed, 12 xfailed, 0 XPASS**. Тести для Р-08 розділено на параметризовані класи і межі; Р-17 має одну параметризовану таблицю; Р-18 — послідовність дозволених дій і один параметризований тест недопустимих пар. В кожному недопустимому переході перевіряється виняток та незмінність статусу й оцінок.

| Випадок ЛР 3 | Pytest-тест (суфікс ID) | Результат | Issue |
|---|---|---|---|
| ТВ-EP-01 | `test_equivalence_classes[ТВ-EP-01]` | passed | - |
| ТВ-EP-02 | `test_equivalence_classes[ТВ-EP-02]` | passed | - |
| ТВ-EP-03 | `test_equivalence_classes[ТВ-EP-03]` | passed | - |
| ТВ-EP-04 | `test_equivalence_classes[ТВ-EP-04]` | xfail | [#12](https://github.com/asiaglh/testing-course-halukh/issues/12) |
| ТВ-EP-05 | `test_equivalence_classes[ТВ-EP-05]` | xfail | [#12](https://github.com/asiaglh/testing-course-halukh/issues/12) |
| ТВ-EP-06 | `test_equivalence_classes[ТВ-EP-06]` | xfail | [#12](https://github.com/asiaglh/testing-course-halukh/issues/12) |
| ТВ-EP-07 | `test_equivalence_classes[ТВ-EP-07]` | xfail | [#12](https://github.com/asiaglh/testing-course-halukh/issues/12) |
| ТВ-EP-08 | `test_equivalence_classes[ТВ-EP-08]` | xfail | [#12](https://github.com/asiaglh/testing-course-halukh/issues/12) |
| ТВ-EP-09 | `test_equivalence_classes[ТВ-EP-09]` | xfail | [#13](https://github.com/asiaglh/testing-course-halukh/issues/13) |
| ТВ-EP-10 | `test_equivalence_classes[ТВ-EP-10]` | passed | - |
| ТВ-EP-11 | `test_equivalence_classes[ТВ-EP-11]` | passed | - |
| ТВ-BVA-01 | `test_boundary_values[ТВ-BVA-01]` | passed | - |
| ТВ-BVA-02 | `test_boundary_values[ТВ-BVA-02]` | passed | - |
| ТВ-BVA-03 | `test_boundary_values[ТВ-BVA-03]` | passed | - |
| ТВ-BVA-04 | `test_boundary_values[ТВ-BVA-04]` | xfail | [#14](https://github.com/asiaglh/testing-course-halukh/issues/14) |
| ТВ-BVA-05 | `test_boundary_values[ТВ-BVA-05]` | passed | - |
| ТВ-BVA-06 | `test_boundary_values[ТВ-BVA-06]` | passed | - |
| ТВ-DT-01 | `test_decision_table[ТВ-DT-01]` | passed | - |
| ТВ-DT-02 | `test_decision_table[ТВ-DT-02]` | passed | - |
| ТВ-DT-03 | `test_decision_table[ТВ-DT-03]` | passed | - |
| ТВ-DT-04 | `test_decision_table[ТВ-DT-04]` | passed | - |
| ТВ-DT-05 | `test_decision_table[ТВ-DT-05]` | passed | - |
| ТВ-DT-06 | `test_decision_table[ТВ-DT-06]` | passed | - |
| ТВ-DT-07 | `test_decision_table[ТВ-DT-07]` | xfail | [#15](https://github.com/asiaglh/testing-course-halukh/issues/15) |
| ТВ-DT-08 | `test_decision_table[ТВ-DT-08]` | passed | - |
| ТВ-DT-09 | `test_decision_table[ТВ-DT-09]` | passed | - |
| ТВ-DT-10 | `test_decision_table[ТВ-DT-10]` | passed | - |
| ТВ-DT-11 | `test_decision_table[ТВ-DT-11]` | passed | - |
| ТВ-DT-12 | `test_decision_table[ТВ-DT-12]` | passed | - |
| ТВ-DT-13 | `test_decision_table[ТВ-DT-13]` | passed | - |
| ТВ-DT-14 | `test_decision_table[ТВ-DT-14]` | passed | - |
| ТВ-DT-15 | `test_decision_table[ТВ-DT-15]` | passed | - |
| ТВ-DT-16 | `test_decision_table[ТВ-DT-16]` | passed | - |
| ТВ-DT-17 | `test_decision_table[ТВ-DT-17]` | passed | - |
| ТВ-DT-18 | `test_decision_table[ТВ-DT-18]` | passed | - |
| ТВ-DT-19 | `test_decision_table[ТВ-DT-19]` | xfail | [#18](https://github.com/asiaglh/testing-course-halukh/issues/18) |
| ТВ-ST-01 | `test_valid_transition_sequence` | passed | - |
| ТВ-ST-02 | `test_invalid_transitions[ТВ-ST-02]` | passed | - |
| ТВ-ST-03 | `test_invalid_transitions[ТВ-ST-03]` | passed | - |
| ТВ-ST-04 | `test_invalid_transitions[ТВ-ST-04]` | passed | - |
| ТВ-ST-05 | `test_invalid_transitions[ТВ-ST-05]` | passed | - |
| ТВ-ST-06 | `test_invalid_transitions[ТВ-ST-06]` | passed | - |
| ТВ-ST-07 | `test_invalid_transitions[ТВ-ST-07]` | passed | - |
| ТВ-ST-08 | `test_invalid_transitions[ТВ-ST-08]` | xfail | [#16](https://github.com/asiaglh/testing-course-halukh/issues/16) |
| ТВ-ST-09 | `test_invalid_transitions[ТВ-ST-09]` | passed | - |
| ТВ-ST-10 | `test_invalid_transitions[ТВ-ST-10]` | passed | - |
| ТВ-ST-11 | `test_invalid_transitions[ТВ-ST-11]` | passed | - |
| ТВ-ST-12 | `test_invalid_transitions[ТВ-ST-12]` | passed | - |
| ТВ-ST-13 | `test_invalid_transitions[ТВ-ST-13]` | passed | - |
| ТВ-ST-14 | `test_invalid_transitions[ТВ-ST-14]` | passed | - |
| ТВ-ST-15 | `test_invalid_transitions[ТВ-ST-15]` | passed | - |
| ТВ-ST-16 | `test_invalid_transitions[ТВ-ST-16]` | xfail | [#17](https://github.com/asiaglh/testing-course-halukh/issues/17) |
| ТВ-ST-17 | `test_invalid_transitions[ТВ-ST-17]` | passed | - |
| ТВ-ST-18 | `test_invalid_transitions[ТВ-ST-18]` | passed | - |
| ТВ-ST-19 | `test_invalid_transitions[ТВ-ST-19]` | xfail | [#16](https://github.com/asiaglh/testing-course-halukh/issues/16) |
