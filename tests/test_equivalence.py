from app.math_core.equivalence import are_equivalent_equations
from app.math_core.sympy_parser import parse_equation


def test_equivalent_equations_direct():
    before_eq = parse_equation("2x + 6 = 10")
    after_eq = parse_equation("2x = 4")

    assert are_equivalent_equations(before_eq, after_eq) is True


def test_equivalent_equations_scaled():
    before_eq = parse_equation("x = 2")
    after_eq = parse_equation("2x = 4")

    assert are_equivalent_equations(before_eq, after_eq) is True


def test_invalid_equations():
    before_eq = parse_equation("2x + 6 = 10")
    after_eq = parse_equation("2x = 16")

    assert are_equivalent_equations(before_eq, after_eq) is False
