# Campaign diagnostics for fatigue and possible donor contamination.

import numpy as np

from .simulation import MarketPanel


def fatigue_diagnostics(panel: MarketPanel) -> dict[str, float | int | str]:
    treated = np.flatnonzero(panel.treated)
    post_weeks = np.flatnonzero(panel.post)
    frequency = panel.frequency[np.ix_(treated, post_weeks)].ravel()
    incremental = panel.true_incremental[np.ix_(treated, post_weeks)].ravel()
    slope = float(np.polyfit(frequency, incremental, 1)[0])
    peak_index = int(np.argmax(np.mean(panel.true_incremental[treated][:, panel.post], axis=0)))
    return {
        "effect_per_frequency": slope,
        "peak_week": int(post_weeks[peak_index] + 1),
        "status": "FATIGUE DETECTED" if slope < -0.5 else "STABLE",
    }


def spillover_sensitivity(lift: float, contamination_range: tuple[float, float] = (0, 0.35)) -> dict[str, float]:
    low, high = contamination_range
    return {
        "assumed_min_contamination": low,
        "assumed_max_contamination": high,
        "reported_lift": lift,
        "corrected_lift_low": lift / (1 - low),
        "corrected_lift_high": lift / (1 - high),
    }

