"""Diminishing-return budget optimization with uncertainty penalty."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


@dataclass(frozen=True)
class Allocation:
    market: str
    budget: float
    expected_incremental: float
    marginal_return: float


def optimize_budget(
    markets: list[str], lifts: np.ndarray, uncertainty: np.ndarray, total_budget: float
) -> list[Allocation]:
    if total_budget <= 0:
        raise ValueError("total_budget must be positive")
    lifts = np.maximum(np.asarray(lifts), 0.1)
    risk_adjusted = np.maximum(0.1, lifts - 0.35 * np.asarray(uncertainty))
    scale = np.linspace(130_000, 230_000, len(markets))
    minimum, maximum = 0.04 * total_budget, 0.40 * total_budget

    def response(budget):
        return risk_adjusted * scale * np.log1p(budget / scale)

    result = minimize(
        lambda budget: -float(np.sum(response(budget))),
        np.full(len(markets), total_budget / len(markets)),
        method="SLSQP",
        bounds=[(minimum, maximum)] * len(markets),
        constraints={"type": "eq", "fun": lambda budget: np.sum(budget) - total_budget},
    )
    if not result.success:
        raise RuntimeError(result.message)
    expected = response(result.x)
    marginal = risk_adjusted / (1 + result.x / scale)
    return [
        Allocation(name, float(budget), float(value), float(mr))
        for name, budget, value, mr in zip(markets, result.x, expected, marginal, strict=True)
    ]

