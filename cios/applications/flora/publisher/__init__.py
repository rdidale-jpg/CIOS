"""Flora Publisher v0.1 executive publication engine."""

__all__ = ["generate_morning_edition"]


def generate_morning_edition(*args, **kwargs):
    """Proxy to the Morning Edition generator without eager module loading."""
    from cios.applications.flora.publisher.morning_edition import generate_morning_edition as _generate

    return _generate(*args, **kwargs)
