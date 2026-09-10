LEVELS = {
    "beginner": {
        "name": "Beginner",
        "seconds": 600,
    },
    "intermediate": {
        "name": "Intermediate",
        "seconds": 300,
    },
    "advanced": {
        "name": "Advanced",
        "seconds": 120,
    },
    "pro": {
        "name": "Pro",
        "seconds": 60,
    },
}


def get_level(name):
    if name not in LEVELS:
        raise ValueError("Invalid difficulty level")

    return LEVELS[name]


def get_time_limit(name):
    if name not in LEVELS:
        raise ValueError("Invalid difficulty level")

    return LEVELS[name]["seconds"]
