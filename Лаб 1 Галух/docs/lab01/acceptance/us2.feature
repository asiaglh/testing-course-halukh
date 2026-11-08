# language: en
@US2
Feature: Administrator adds a student who can access the system

  @S2-01 @R01 @R02 @R15
  Scenario: Valid student is created and linked to the university identity
    Given an administrator is authenticated and group "63M" exists
    And no student has normalized email "anna@university.example"
    When the administrator creates "Anna Halukh" with email "Anna@university.example", group "63M" and entry year 2026
    Then the API responds with status 201 and a new student ID
    And one active student stores normalized email "anna@university.example"
    When the trusted IdP authenticates the verified identity linked to that student ID
    Then the student session is created with the student role
    And the student can open their own dashboard

  @S2-02 @R02
  Scenario Outline: Normalized duplicate email is rejected
    Given an administrator is authenticated
    And a student already has email "anna@university.example"
    When the administrator submits an otherwise valid student with email input <email_input>
    Then the API responds with status 409 and identifies the duplicate email
    And no additional student is created
    Examples:
      | email_input                              |
      | "anna@university.example"                 |
      | "ANNA@university.example"                 |
      | " anna@university.example "               |

  @S2-03 @R01
  Scenario Outline: Invalid required data prevents creation
    Given an administrator is authenticated
    When the administrator submits an otherwise valid student with <invalid_data>
    Then the API responds with status 422 and identifies the invalid field
    And no student is created
    Examples:
      | invalid_data                    |
      | a missing full name             |
      | a malformed email               |
      | an unknown group                |
      | entry year 1999                 |
      | entry year after the current year |

  @S2-04 @R01 @R12 @R15
  Scenario Outline: Creation requires an administrator session
    Given the caller has <session>
    When the caller submits a valid student through POST /api/students
    Then the API responds with status <status>
    And no student is created
    Examples:
      | session               | status |
      | no session            | 401    |
      | a student session     | 403    |
      | a teacher session     | 403    |
      | an expired OIDC token | 401    |

  @S2-05 @R02
  Scenario: Concurrent duplicate creation has one winner
    Given two authenticated administrators and no student with email "new@university.example"
    When both simultaneously create otherwise valid students with that normalized email
    Then exactly one response has status 201 and the other has status 409
    And exactly one student has that email

  @S2-06 @R01 @R03 @R14
  Scenario: Administrator finds students at the specified data volume
    Given 5000 active students and 100000 current grades exist
    And the load environment and profile match QV04 in the quality requirements
    When 150 authenticated sessions request GET /api/students with group filters and page size 50 for 15 minutes after warmup
    Then every successful page contains at most 50 records matching the requested group
    And response time p95 is at most 500 milliseconds in each of 3 runs
    And the proportion of server failures is below 1 percent in each run

  @S2-07 @R15 @R16
  Scenario: Controlled IdP enforces the proposed lockout policy
    Given the configured university IdP enforces policy A-08 and its clock is controlled
    And an active student's password failure count is zero
    When the student submits two incorrect passwords within 10 minutes
    Then the identity is not yet locked
    When the student submits a third incorrect password within that window
    Then authentication is locked for 15 minutes and no application session is created
    When the correct password is submitted 14 minutes 59 seconds after lockout
    Then authentication is refused and the lockout deadline is unchanged
    When the correct password is submitted exactly 15 minutes after lockout
    Then authentication succeeds and the failure counter resets

  @S2-08 @R01 @R02
  Scenario: Administrator reads updates and deactivates a student without deleting grades
    Given an administrator is authenticated and an active student has a stored grade
    When the administrator reads that student by ID
    Then the API responds with status 200 and the stored student fields
    When the administrator updates the student to an existing group and a unique valid email
    Then the API responds with status 200 and subsequent reads show the updated fields
    When the administrator sends DELETE for that student
    Then the API responds with status 204 and the student becomes inactive
    And the existing grade and audit history remain stored
    And a new grade request for that student is rejected with status 409
    And that student's new login is rejected with status 403
