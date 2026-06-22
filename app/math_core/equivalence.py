from sympy import simplify

from app.math_core.sympy_parser import ParsedEquation, equation_to_normal_form


def are_equivalent_expressions(expr1, expr2) -> bool:
    try:
        return simplify(expr1 - expr2) == 0
    except Exception:
        return False


def _is_nonzero_constant(expr) -> bool:
    simplified = simplify(expr)

    if simplified == 0:
        return False

    if getattr(simplified, "free_symbols", None):
        return False

    if simplified.is_finite is False:
        return False

    return True


def are_equivalent_equations(before_eq: ParsedEquation, after_eq: ParsedEquation) -> bool:
    before_nf = equation_to_normal_form(before_eq)
    after_nf = equation_to_normal_form(after_eq)

    if before_nf == 0 and after_nf == 0:
        return True

    if are_equivalent_expressions(before_nf, after_nf):
        return True

    if are_equivalent_expressions(before_nf, -after_nf):
        return True

    if before_nf == 0 or after_nf == 0:
        return False

    try:
        ratio = simplify(before_nf / after_nf)
    except Exception:
        return False

    return _is_nonzero_constant(ratio)
