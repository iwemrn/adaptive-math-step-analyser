from app.services.diagnosis_service import diagnose_transition


def test_diagnose_equivalent_transition():
    result = diagnose_transition(
        before_text="2x + 6 = 10",
        after_text="2x = 4",
        is_valid=True,
    )

    assert result.diagnosis_code == "equivalent_transition"
    assert result.error_probs == {}


def test_diagnose_sign_error():
    result = diagnose_transition(
        before_text="2x + 6 = 10",
        after_text="2x = 16",
        is_valid=False,
    )

    assert result.diagnosis_code == "sign_error"
    assert "sign_error" in result.error_probs


def test_diagnose_arithmetic_error():
    result = diagnose_transition(
        before_text="2x = 4",
        after_text="x = 4",
        is_valid=False,
    )

    assert result.diagnosis_code == "arithmetic_error"
    assert "arithmetic_error" in result.error_probs


def test_diagnose_invalid_transform():
    result = diagnose_transition(
        before_text="x**2 = 4",
        after_text="x = 2",
        is_valid=False,
    )

    assert result.diagnosis_code == "invalid_transform"
    assert "invalid_transform" in result.error_probs
