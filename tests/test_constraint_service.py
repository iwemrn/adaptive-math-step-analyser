from app.services.constraint_service import (
    check_single_expression_constraints,
    check_transition_constraints,
)


def test_detect_possible_domain_loss():
    result = check_transition_constraints(
        "(x**2 - 1)/(x - 1) = 2",
        "x + 1 = 2",
    )

    assert result.violation_code == "possible_domain_loss"
    assert "possible_domain_loss" in result.error_probs


def test_detect_division_by_zero_in_single_expression():
    result = check_single_expression_constraints("1/0")

    assert result.violation_code == "division_by_zero"
    assert "division_by_zero" in result.error_probs
