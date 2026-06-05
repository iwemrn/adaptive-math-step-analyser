def analyze_step_stub(raw_text: str) -> dict:
    """
    Временная заглушка анализа шага.
    Позже здесь будет:
    - нормализация шага,
    - разбор через parser,
    - SymPy,
    - проверка ограничений,
    - диагностика ошибок.
    """
    return {
        "is_valid": True,
        "soft_score": 0.8,
        "math_score": 0.8,
        "logic_score": 0.8,
        "condition_score": 0.8,
        "goal_score": 0.8,
        "operation_type": "pending_analysis",
        "feedback": {
            "type": "confirm",
            "text": "Шаг принят в обработку"
        },
        "error_probs": {},
    }
