from datetime import datetime, timedelta


def sm2(quality: int, repetitions: int, ease_factor: float, interval: int):
    """Run the SM-2 algorithm and return updated scheduling parameters.

    Args:
        quality: Response quality (0-5).
        repetitions: Current repetition count.
        ease_factor: Current ease factor.
        interval: Current interval in days.

    Returns:
        Tuple of (new_repetitions, new_ease_factor, new_interval, next_review).
    """
    # Adjust ease factor (always applied)
    new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(1.3, new_ef)

    if quality >= 3:
        # Correct response — advance schedule
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)
        new_reps = repetitions + 1
    else:
        # Incorrect response — reset
        new_interval = 1
        new_reps = 0

    next_review = datetime.utcnow() + timedelta(days=new_interval)
    return new_reps, new_ef, new_interval, next_review
