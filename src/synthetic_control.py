# Synthetic control estimation and market placebo inference.

from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
from .simulation import MarketPanel


@dataclass(frozen=True)
class MarketEstimate:
    market: str
    lift: float
    relative_lift: float
    pre_rmse: float
    post_rmse: float
    placebo_p: float
    top_donors: tuple[tuple[str, float], ...]


def donor_weights(target_pre: np.ndarray, donors_pre: np.ndarray) -> np.ndarray:
    n = donors_pre.shape[0]
    scale = max(float(np.std(target_pre)), 1.0)

    def objective(weights: np.ndarray) -> float:
        residual = (target_pre - weights @ donors_pre) / scale
        return float(np.mean(residual**2))

    result = minimize(
        objective,
        np.full(n, 1 / n),
        method="SLSQP",
        bounds=[(0.0, 1.0)] * n,
        constraints={"type": "eq", "fun": lambda w: np.sum(w) - 1},
        options={"maxiter": 2_000, "ftol": 1e-10},
    )
    if not result.success:
        raise RuntimeError(f"Synthetic-control optimization failed: {result.message}")
    return result.x


def _gap(target: np.ndarray, donors: np.ndarray, pre: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    weights = donor_weights(target[pre], donors[:, pre])
    return target - weights @ donors, weights


def estimate_markets(panel: MarketPanel) -> list[MarketEstimate]:
    pre = ~panel.post
    donor_ids = np.flatnonzero(~panel.treated)
    estimates = []
    for target_id in np.flatnonzero(panel.treated):
        gap, weights = _gap(panel.outcomes[target_id], panel.outcomes[donor_ids], pre)
        observed_lift = float(np.mean(gap[panel.post]))
        placebo_lifts = []
        for placebo_id in donor_ids:
            placebo_donors = donor_ids[donor_ids != placebo_id]
            placebo_gap, _ = _gap(
                panel.outcomes[placebo_id], panel.outcomes[placebo_donors], pre
            )
            placebo_lifts.append(abs(float(np.mean(placebo_gap[panel.post]))))
        p_value = (1 + sum(value >= abs(observed_lift) for value in placebo_lifts)) / (
            1 + len(placebo_lifts)
        )
        counterfactual_mean = float(np.mean(panel.outcomes[target_id, panel.post] - gap[panel.post]))
        ranked = np.argsort(weights)[::-1][:3]
        estimates.append(
            MarketEstimate(
                market=panel.markets[target_id],
                lift=observed_lift,
                relative_lift=observed_lift / counterfactual_mean,
                pre_rmse=float(np.sqrt(np.mean(gap[pre] ** 2))),
                post_rmse=float(np.sqrt(np.mean(gap[panel.post] ** 2))),
                placebo_p=float(p_value),
                top_donors=tuple(
                    (panel.markets[donor_ids[index]], float(weights[index])) for index in ranked
                ),
            )
        )
    return estimates
