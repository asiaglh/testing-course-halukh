# language: en
@US1
Feature: Teacher records scores and the system derives ECTS
  # Proposed baseline A-03 and A-05; not an executed test suite.
  Background:
    Given an active student is enrolled in the teacher's assigned discipline
    And the teacher has a valid authenticated session

  @S1-01 @R04 @R05 @QV01
  Scenario Outline: Every boundary of the ECTS scale is mapped correctly
    Given the student has no grade for that discipline
    When the teacher submits the integer score <score> through POST /api/grades
    Then the API responds with status 201
    And the stored score is <score> and ECTS is "<ects>"
    And the student's dashboard displays that score and ECTS
    Examples:
      | score | ects |
      | 0     | Fx   |
      | 1     | Fx   |
      | 59    | Fx   |
      | 60    | E    |
      | 66    | E    |
      | 67    | D    |
      | 74    | D    |
      | 75    | C    |
      | 81    | C    |
      | 82    | B    |
      | 89    | B    |
      | 90    | A    |
      | 100   | A    |

  @S1-02 @R04 @R09
  Scenario Outline: Invalid score input is rejected without changing data
    Given the student has no grade for that discipline
    When the teacher submits a score field represented by <input>
    Then the API responds with status 422
    And no grade or successful-change audit event is created
    And the UI identifies the score field and states that an integer from 0 to 100 is required
    Examples:
      | input          |
      | -1             |
      | 101            |
      | 59.5           |
      | null           |
      | a JSON string  |
      | a missing field|

  @S1-03 @R04 @R12
  Scenario: Teacher cannot record a score in an unassigned discipline
    Given the student has no grade in another discipline not assigned to this teacher
    When the teacher submits 80 points for that other discipline
    Then the API responds with status 403
    And no grade or successful-change audit event is created

  @S1-04 @R08 @R13
  Scenario Outline: The correction window has an inclusive upper boundary
    Given the grade was created at "2026-10-01T10:00:00Z" with score 70 and version 1
    And the server clock is "<now>"
    When the teacher patches the score to 90 with expected version 1 and reason "Input correction"
    Then the API responds with status <status>
    And the current score is <score> and version is <version>
    And the number of new successful-change audit events is <events>
    And the grade creation timestamp remains "2026-10-01T10:00:00Z"
    Examples:
      | now                  | status | score | version | events |
      | 2026-10-03T09:59:59Z | 200    | 90    | 2       | 1      |
      | 2026-10-03T10:00:00Z | 200    | 90    | 2       | 1      |
      | 2026-10-03T10:00:01Z | 409    | 70    | 1       | 0      |

  @S1-05 @R08 @R13
  Scenario: Concurrent corrections cannot silently overwrite each other
    Given a grade has score 70 and version 1 within its correction window
    When two authorized requests concurrently patch it to 80 and 90 with expected version 1
    Then exactly one response has status 200 and the other has status 409
    And the stored score equals the successful request's score with its matching ECTS
    And the current version is 2
    And exactly one new audit event records grade ID, teacher ID, UTC timestamp, old score, new score, version and reason

  @S1-06 @R13
  Scenario: Audit failure rolls back the grade and acknowledged data survives restart
    Given a grade has score 70 and version 1 within its correction window
    And the next audit insert is forced to fail
    When the teacher patches the score to 90 with expected version 1 and a reason
    Then the API responds with status 503 without a success message
    And the grade remains at score 70 and version 1 with no new successful-change audit event
    When the audit failure is removed and the same authorized patch succeeds
    Then score 90 with ECTS "A" and version 2 is acknowledged
    When the database process is stopped abruptly with its disk preserved and restarted
    Then the same acknowledged grade and its complete audit event are readable within 10 minutes

  @S1-07 @R04
  Scenario: A repeated creation cannot replace an existing grade
    Given the student already has score 70 in that discipline
    When the teacher submits 90 points for the same student and discipline through POST /api/grades
    Then the API responds with status 409
    And the existing grade and its audit history remain unchanged
