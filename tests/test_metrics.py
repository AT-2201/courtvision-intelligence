from courtvision.analytics.metrics import per_100, possessions, true_shooting_percentage


def test_true_shooting_percentage() -> None:
    assert true_shooting_percentage(30, 20, 10) == 0.6148


def test_possession_metrics_handle_zero() -> None:
    assert possessions(0, 0, 0, 0) == 0
    assert per_100(12, 0) == 0
