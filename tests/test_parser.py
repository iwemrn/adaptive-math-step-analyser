from app.math_core.parser import parse_step


def test_parse_transition_step():
    parsed = parse_step("2x + 6 = 10 => 2x = 4")

    assert parsed.before_text == "2x + 6 = 10"
    assert parsed.after_text == "2x = 4"
    assert parsed.operation_type == "parsed_transition"


def test_parse_single_expression():
    parsed = parse_step("2x = 4")

    assert parsed.before_text is None
    assert parsed.after_text == "2x = 4"
    assert parsed.operation_type == "single_expression"
