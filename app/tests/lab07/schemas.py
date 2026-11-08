"""Independent response schemas derived from R-23, not from OpenAPI code."""

STUDENT_SCHEMA = {
    "type": "object",
    "required": ["id", "first_name", "last_name", "email", "group", "average"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
        "email": {"type": "string", "format": "email"},
        "group": {"type": "string"},
        "average": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
    },
    "additionalProperties": False,
}

GRADE_SCHEMA = {
    "type": "object",
    "required": ["course", "score", "ects", "graded_on"],
    "properties": {
        "course": {"type": "string", "minLength": 1, "maxLength": 100},
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "ects": {"enum": ["A", "B", "C", "D", "E", "Fx"]},
        "graded_on": {"type": "string", "format": "date"},
    },
    "additionalProperties": False,
}
