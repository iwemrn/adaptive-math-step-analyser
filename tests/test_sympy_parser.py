from app.math_core.sympy_parser import parse_equation


def test_parse_equation_with_implicit_multiplication():
    eq = parse_equation("2x + 6 = 10")

    assert eq.left_text == "2x + 6"
    assert eq.right_text == "10"
    assert str(eq.left_expr) == "2*x + 6"
    assert str(eq.right_expr) == "10"
