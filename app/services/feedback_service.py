def build_feedback(diagnosis_code: str, is_valid: bool) -> dict:
    if diagnosis_code == "equivalent_transition":
        return {
            "type": "confirm",
            "text": "Преобразование математически корректно.",
        }

    if diagnosis_code == "sign_error":
        return {
            "type": "explain_error",
            "text": "Вероятно, допущена ошибка знака при переносе слагаемого.",
        }

    if diagnosis_code == "arithmetic_error":
        return {
            "type": "explain_error",
            "text": "Идея шага похожа на верную, но в вычислении допущена арифметическая ошибка.",
        }

    if diagnosis_code == "invalid_transform":
        return {
            "type": "explain_error",
            "text": "Преобразование изменяет множество решений и не является равносильным.",
        }

    if diagnosis_code == "division_by_zero":
        return {
            "type": "explain_error",
            "text": "В шаге обнаружено деление на ноль. Такое преобразование недопустимо.",
        }

    if diagnosis_code == "possible_domain_loss":
        return {
            "type": "warning",
            "text": "Преобразование похоже на сокращение дроби или устранение знаменателя. Возможно, потеряно ограничение области допустимых значений.",
        }

    if diagnosis_code == "math_parse_error":
        return {
            "type": "explain_error",
            "text": "Не удалось математически разобрать шаг. Проверь запись выражения.",
        }

    if diagnosis_code == "parse_error":
        return {
            "type": "explain_error",
            "text": "Не удалось разобрать структуру шага. Используй формат 'до => после'.",
        }

    if diagnosis_code == "single_expression":
        return {
            "type": "hint",
            "text": "Выражение распознано. Для проверки преобразования лучше использовать формат 'до => после'.",
        }

    if is_valid:
        return {
            "type": "confirm",
            "text": "Шаг распознан корректно.",
        }

    return {
        "type": "explain_error",
        "text": "В шаге обнаружена ошибка.",
    }
