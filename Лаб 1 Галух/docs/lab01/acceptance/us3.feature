# language: en
@US3
Feature: Student views their own grades

  @S3-01 @R06
  Scenario: Student sees current own scores and ECTS
    Given an active student has a valid session
    And that student has score 90 with ECTS "A" and score 59 with ECTS "Fx" in two disciplines
    When the student opens their dashboard
    Then the API responds with status 200
    And the dashboard shows both discipline names, scores, ECTS and last-change timestamps
    And no other student's grade is present

  @S3-02 @R06 @R07 @R12
  Scenario Outline: Changing the student ID cannot reveal another student's data
    Given an active student has a valid session
    And another student belongs to <group_relation>
    When the first student requests the other student's <resource>
    Then the API responds with status 403
    And the response contains none of the other student's personal fields or grades
    Examples:
      | group_relation | resource        |
      | the same group | grades endpoint |
      | another group  | grades endpoint |
      | the same group | profile endpoint|
      | another group  | profile endpoint|

  @S3-03 @R06 @R15
  Scenario Outline: Invalid or unlinked identity cannot view grades
    Given the caller presents <identity>
    When the caller requests a student's grades
    Then the API responds with status <status>
    And no grade or personal data is returned
    Examples:
      | identity                          | status |
      | no authentication                 | 401    |
      | an expired token                  | 401    |
      | a token with a forged signature   | 401    |
      | a token with the wrong issuer     | 401    |
      | a token with the wrong audience   | 401    |
      | a trusted but unlinked identity   | 403    |
      | a trusted but unverified email    | 403    |

  @S3-04 @R06
  Scenario: A new student without grades sees a clear empty state
    Given an active student has a valid session and no grades
    When the student opens their dashboard
    Then the grades API responds with status 200 and an empty array
    And the dashboard displays "Оцінок поки немає"
    And no score of zero is fabricated

  @S3-05 @R07 @R12 @R13
  Scenario Outline: A student cannot access administrative resources
    Given an active student has a valid session
    When the student sends <request>
    Then the API responds with status 403
    And no protected data is returned and no stored data is changed
    Examples:
      | request                                      |
      | GET /api/students                            |
      | GET /api/groups/63/report?format=pdf          |
      | GET /api/groups/63/report?format=xlsx         |
      | GET /api/audit/grades                        |
      | PUT /api/students/another-id                 |
      | DELETE /api/students/another-id              |
      | POST /api/grades                             |

  # Supporting administrator scenario is included to cover report requirements outside US-1..US-3.
  @S3-06 @R11
  Scenario Outline: Administrator exports a consistent group report
    Given an administrator is authenticated
    And an existing group contains 30 students with Cyrillic names and all ECTS categories
    And an expected database snapshot is captured when report generation starts
    When the administrator requests that group's report in "<format>" format
    And another teacher changes a score after the report snapshot starts
    Then the API responds with status 200 and a valid "<format>" file
    And the report shows the group, UTC date, student names, disciplines, scores and ECTS from the snapshot
    And no expected row is missing or duplicated
    Examples:
      | format |
      | pdf    |
      | xlsx   |

  @S3-07 @R11
  Scenario Outline: Report edge cases follow the explicit contract
    Given an administrator is authenticated
    When the administrator requests <report>
    Then the API responds with status <status>
    And the result is <result>
    Examples:
      | report                      | status | result                       |
      | an empty group as pdf       | 200    | a valid file with headers    |
      | an empty group as xlsx      | 200    | a valid file with headers    |
      | a nonexistent group as pdf  | 404    | an error without report data |
      | an existing group as csv    | 422    | an error without report data |
