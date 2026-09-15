"""Privacy-safe market panel with known campaign effects and spillovers."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MarketPanel:
    markets: tuple[str, ...]
    weeks: np.ndarray
    outcomes: np.ndarray
    spend: np.ndarray
    treated: np.ndarray
    post: np.ndarray
    creator_share: np.ndarray
    frequency: np.ndarray
    true_incremental: np.ndarray


def simulate_panel(n_markets: int = 24, n_weeks: int = 26, seed: int = 17) -> MarketPanel:
    if n_markets < 10 or n_weeks < 16:
        raise ValueError("Use at least 10 markets and 16 weeks")
    rng = np.random.default_rng(seed)
    weeks = np.arange(n_weeks)
    post = weeks >= 16
    markets = tuple(f"MKT-{i:02d}" for i in range(1, n_markets + 1))
    treated = np.zeros(n_markets, dtype=bool)
    treated[: max(4, n_markets // 4)] = True

    national = 120 + 2.1 * weeks + 12 * np.sin(weeks / 2.8) + rng.normal(0, 2.5, n_weeks)
    loadings = rng.uniform(0.82, 1.22, n_markets)
    intercepts = rng.normal(15, 8, n_markets)
    outcomes = intercepts[:, None] + loadings[:, None] * national + rng.normal(0, 4.2, (n_markets, n_weeks))
    spend = np.zeros_like(outcomes)
    creator_share = rng.uniform(0.25, 0.82, n_markets)
    frequency = np.zeros_like(outcomes)
    true_incremental = np.zeros_like(outcomes)

    post_index = np.flatnonzero(post)
    for market in np.flatnonzero(treated):
        weekly_spend = rng.uniform(55_000, 125_000, len(post_index))
        spend[market, post] = weekly_spend
        cumulative_frequency = np.cumsum(weekly_spend / rng.uniform(65_000, 90_000))
        frequency[market, post] = cumulative_frequency
        # Creator-led execution lifts response; repeated exposure produces fatigue.
        lift = (14 + 13 * creator_share[market]) * (1 - np.exp(-weekly_spend / 50_000))
        fatigue = np.maximum(0, cumulative_frequency - 6) * 1.25
        effect = np.maximum(1.5, lift - fatigue)
        true_incremental[market, post] = effect
        outcomes[market, post] += effect

    # Two adjacent donor markets receive small content spillovers.
    for market in range(max(4, n_markets // 4), max(4, n_markets // 4) + 2):
        outcomes[market, post] += 2.2

    return MarketPanel(markets, weeks, outcomes, spend, treated, post, creator_share, frequency, true_incremental)

