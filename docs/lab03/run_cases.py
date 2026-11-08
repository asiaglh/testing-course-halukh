"""Execute the previously committed black-box cases through the public API."""

import json
from datetime import date, timedelta
from pathlib import Path

from student_portal.corrections import correct_grade
from student_portal.grades import Grade
from student_portal.people import Funding, Student
from student_portal.scholarship import scholarship
from student_portal.status import Event, Status

HERE = Path(__file__).resolve().parent
SPEC = json.loads((HERE / "spec_cases.json").read_text(encoding="utf-8"))
BASE = date(2026, 10, 1)
RESULTS = {"corrections": [], "scholarship": [], "state": []}


def outcome(call):
    try:
        value = call()
        return {"kind": "value", "value": repr(value)}
    except Exception as exc:  # noqa: BLE001 - record unexpected failures too
        return {"kind": "error", "type": type(exc).__name__, "message": str(exc)}


def student(scores=(), *, funding="BUDGET", status="ACTIVE"):
    grades = [Grade(f"Предмет {i + 1}", score, BASE) for i, score in enumerate(scores)]
    return Student(
        1, "Олена", "Коваль", grades, funding=Funding[funding], status=Status[status]
    )


for case in SPEC["corrections"]:
    original = Grade("Python", 70, BASE)
    try:
        corrected = correct_grade(
            original, case["score"], BASE + timedelta(days=case["d"])
        )
        result = {"kind": "value", "value": repr(corrected)}
        actual_kind = (
            f"Grade:{corrected.score}"
            if corrected.course == "Python" and corrected.graded_on == BASE
            else "WrongGradeFields"
        )
    except Exception as exc:  # noqa: BLE001 - compare the exact observed error type
        result = {"kind": "error", "type": type(exc).__name__, "message": str(exc)}
        actual_kind = result["type"]
    changed_original = (
        original.score != 70
        or original.course != "Python"
        or original.graded_on != BASE
    )
    RESULTS["corrections"].append(
        {
            **case,
            "actual": result,
            "actual_kind": actual_kind,
            "original_unchanged": not changed_original,
            "passed": actual_kind == case["expect"] and not changed_original,
        }
    )


for case in SPEC["scholarship"]:
    s = student(
        case["scores"], funding=case["funding"], status=case.get("status", "ACTIVE")
    )
    try:
        award = scholarship(s)
        result = {"kind": "value", "value": repr(award)}
        actual_kind = award.name
    except Exception as exc:  # noqa: BLE001 - compare the exact observed error type
        result = {"kind": "error", "type": type(exc).__name__, "message": str(exc)}
        actual_kind = result["type"]
    RESULTS["scholarship"].append(
        {
            **case,
            "average": s.average(),
            "has_fx": s.has_debts(),
            "actual": result,
            "actual_kind": actual_kind,
            "passed": actual_kind == case["expect"],
        }
    )


state_spec = SPEC["state"]
s = student()
steps = []
for event_name, expected_status in zip(
    state_spec["valid_sequence"], state_spec["valid_expected"], strict=True
):
    before = {"status": s.status.name, "grades": [repr(g) for g in s.grades]}
    if event_name == "ADD_GRADE":
        result = outcome(lambda current=s: current.add_grade(Grade("Python", 80, BASE)))
    else:
        result = outcome(lambda name=event_name: s.change_status(Event[name]))
    after = {"status": s.status.name, "grades": [repr(g) for g in s.grades]}
    passed_step = result["kind"] == "value" and after["status"] == expected_status
    if event_name == "ADD_GRADE":
        passed_step = passed_step and len(after["grades"]) == len(before["grades"]) + 1
    else:
        passed_step = passed_step and after["grades"] == before["grades"]
    steps.append(
        {
            "event": event_name,
            "expected_status": expected_status,
            "actual": result,
            "before": before,
            "after": after,
            "passed": passed_step,
        }
    )
RESULTS["state"].append(
    {"id": "ТВ-ST-01", "steps": steps, "passed": all(x["passed"] for x in steps)}
)

for case in [state_spec["guard_false"], *state_spec["invalid"]]:
    s = student(case.get("scores", []), status=case["status"])
    before = {"status": s.status.name, "grades": [repr(g) for g in s.grades]}
    if case["event"] == "ADD_GRADE":
        result = outcome(lambda current=s: current.add_grade(Grade("Python", 80, BASE)))
    else:
        result = outcome(
            lambda current=s, name=case["event"]: current.change_status(Event[name])
        )
    after = {"status": s.status.name, "grades": [repr(g) for g in s.grades]}
    expect = case.get("expect", "InvalidTransitionError")
    RESULTS["state"].append(
        {
            **case,
            "expect": expect,
            "actual": result,
            "before": before,
            "after": after,
            "passed": result["kind"] == "error"
            and result["type"] == expect
            and before == after,
        }
    )


out = HERE / "evidence" / "results.json"
out.parent.mkdir(exist_ok=True)
out.write_text(
    json.dumps(RESULTS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
for family, cases in RESULTS.items():
    failed = [case["id"] for case in cases if not case["passed"]]
    print(
        f"{family}: {len(cases) - len(failed)}/{len(cases)} пройдено; не пройдено: {', '.join(failed) or '—'}"
    )
print(out)
