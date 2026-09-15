import numpy as np
import pytest

from brandlift_lab.analysis import analyze
from brandlift_lab.optimizer import optimize_budget
from brandlift_lab.simulation import simulate_panel
from brandlift_lab.synthetic_control import donor_weights, estimate_markets


def test_simulation_is_deterministic_and_has_known_effect():
    first = simulate_panel(seed=5)
    second = simulate_panel(seed=5)
    assert np.array_equal(first.outcomes, second.outcomes)
    assert np.mean(first.true_incremental[first.treated][:, first.post]) > 5


def test_donor_weights_are_convex():
    panel = simulate_panel(seed=4)
    target = panel.outcomes[0, ~panel.post]
    donors = panel.outcomes[~panel.treated][:, ~panel.post]
    weights = donor_weights(target, donors)
    assert np.sum(weights) == pytest.approx(1.0)
    assert np.all(weights >= 0)


def test_synthetic_control_recovers_positive_lift():
    estimates = estimate_markets(simulate_panel(seed=17))
    assert len(estimates) == 6
    assert np.mean([item.lift for item in estimates]) > 8
    assert all(item.pre_rmse < item.post_rmse for item in estimates)


def test_optimizer_spends_exact_budget_with_bounds():
    result = optimize_budget(["a", "b", "c"], np.array([9, 12, 15]), np.array([2, 3, 4]), 1_000_000)
    assert sum(item.budget for item in result) == pytest.approx(1_000_000)
    assert all(40_000 <= item.budget <= 400_000 for item in result)


def test_analysis_contract():
    result = analyze(seed=17, budget=1_000_000)
    assert result["decision"]["status"] in {"SCALE", "SCALE WITH ROTATION", "ITERATE", "HOLD"}
    assert len(result["allocation"]) == result["campaign"]["treated_markets"]
    assert len(result["assumptions"]) >= 4

