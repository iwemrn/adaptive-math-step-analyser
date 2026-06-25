from app.models.student_profile import StudentProfile


DIAGNOSIS_RECOMMENDATIONS = {
    "sign_error": {
        "code": "practice_sign_error",
        "title": "Потренировать перенос слагаемых",
        "description": "У пользователя часто встречается ошибка знака при переносе. Нужны задания на преобразование линейных уравнений по шагам.",
    },
    "arithmetic_error": {
        "code": "practice_arithmetic",
        "title": "Потренировать вычисления",
        "description": "Стоит дать короткие задания на вычисления и деление/умножение обеих частей уравнения.",
    },
    "invalid_transform": {
        "code": "practice_equivalent_transforms",
        "title": "Повторить равносильные преобразования",
        "description": "Нужно укрепить понимание того, какие преобразования сохраняют множество решений.",
    },
    "possible_domain_loss": {
        "code": "practice_domain_constraints",
        "title": "Повторить ОДЗ и сокращение дробей",
        "description": "Нужно закрепить тему области допустимых значений и аккуратной работы со знаменателями.",
    },
    "division_by_zero": {
        "code": "practice_division_constraints",
        "title": "Повторить недопустимые операции",
        "description": "Следует отдельно разобрать, почему деление на ноль запрещено и как его избегать.",
    },
    "parse_error": {
        "code": "practice_step_format",
        "title": "Уточнить формат записи шага",
        "description": "Полезно напомнить пользователю использовать формат 'до => после' и аккуратную математическую запись.",
    },
    "math_parse_error": {
        "code": "practice_math_notation",
        "title": "Уточнить математическую запись",
        "description": "Следует потренировать более корректную запись выражений и уравнений.",
    },
}


def _topic_title(topic: str) -> str:
    return topic.replace("_", " ")


def build_recommendations(profile: StudentProfile) -> list[dict]:
    recommendations: list[dict] = []

    if profile.total_steps == 0:
        return [
            {
                "code": "start_practice",
                "title": "Начать тренировку",
                "description": "Профиль пока пуст. Выполни несколько шагов решения, чтобы система начала подстраивать рекомендации.",
            }
        ]

    misconception_stats = dict(profile.misconception_stats_json or {})
    sorted_misconceptions = sorted(
        misconception_stats.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for diagnosis_code, _count in sorted_misconceptions[:2]:
        recommendation = DIAGNOSIS_RECOMMENDATIONS.get(diagnosis_code)
        if recommendation:
            recommendations.append(recommendation)

    topic_stats = dict(profile.topic_mastery_json or {})
    weak_topics = []

    for topic, stats in topic_stats.items():
        mastery = stats.get("mastery", 0.0)
        total_steps = stats.get("total_steps", 0)
        if total_steps > 0 and mastery < 0.75:
            weak_topics.append((topic, mastery))

    weak_topics.sort(key=lambda item: item[1])

    for topic, mastery in weak_topics[:2]:
        recommendations.append(
            {
                "code": f"practice_topic_{topic}",
                "title": f"Повторить тему: {_topic_title(topic)}",
                "description": f"Текущий уровень освоения темы '{_topic_title(topic)}' около {round(mastery * 100)}%. Полезно дать дополнительные тренировочные задания.",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "code": "continue_practice",
                "title": "Продолжить тренировку",
                "description": "Сейчас серьёзных проблем не видно. Можно постепенно усложнять задания и расширять набор тем.",
            }
        )

    return recommendations
