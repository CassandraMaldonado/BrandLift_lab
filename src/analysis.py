"""End-to-end causal evidence brief and decision policy."""

from dataclasses import asdict

import numpy as np

from .diagnostics import fatigue_diagnostics, spillover_sensitivity
from .optimizer import optimize_budget
from .simulation import simulate_panel
from .synthetic_control import donor_weights, estimate_markets


def analyze(seed: int = 17, budget: float = 1_000_000) -> dict:
    panel = simulate_panel(seed=seed)
    estimates = estimate_markets(panel)
    lifts = np.array([item.lift for item in estimates])
    uncertainty = np.array([item.post_rmse for item in estimates])
    allocations = optimize_budget([item.market for item in estimates], lifts, uncertainty, budget)
    donor_ids = np.flatnonzero(~panel.treated)
    synthetic_series = []
    observed_series = []
    for target_id in np.flatnonzero(panel.treated):
        weights = donor_weights(
            panel.outcomes[target_id, ~panel.post],
            panel.outcomes[donor_ids][:, ~panel.post],
        )
        synthetic_series.append(weights @ panel.outcomes[donor_ids])
        observed_series.append(panel.outcomes[target_id])
    aggregate_lift = float(np.mean(lifts))
    average_pre_rmse = float(np.mean([item.pre_rmse for item in estimates]))
    # With 18 donor markets, randomization inference is discrete. Treat p <= .20
    # as directional support for a scaling decision, while exposing exact values.
    significant_share = float(np.mean([item.placebo_p <= 0.20 for item in estimates]))
    fatigue = fatigue_diagnostics(panel)
    sensitivity = spillover_sensitivity(aggregate_lift)

    if average_pre_rmse > 8:
        status = "HOLD"
    elif aggregate_lift > 8 and significant_share >= 0.5:
        status = "SCALE WITH ROTATION" if fatigue["status"] == "FATIGUE DETECTED" else "SCALE"
    else:
        status = "ITERATE"

    return {
        "campaign": {
            "name": "Creator-Led Brand Launch",
            "markets": len(panel.markets),
            "treated_markets": int(np.sum(panel.treated)),
            "pre_weeks": int(np.sum(~panel.post)),
            "post_weeks": int(np.sum(panel.post)),
            "budget": budget,
        },
        "decision": {
            "status": status,
            "headline": f"Estimated incremental lift is {aggregate_lift:.1f} actions per market-week.",
            "next_action": "Scale efficient markets, refresh creative before the detected fatigue point, and retain geographic holdouts.",
        },
        "evidence": {
            "average_lift": aggregate_lift,
            "average_relative_lift": float(np.mean([item.relative_lift for item in estimates])),
            "average_pre_rmse": average_pre_rmse,
            "placebo_supported_share": significant_share,
            "markets": [asdict(item) for item in estimates],
        },
        "fatigue": fatigue,
        "timeline": {
            "weeks": (panel.weeks + 1).tolist(),
            "observed": np.mean(observed_series, axis=0).tolist(),
            "counterfactual": np.mean(synthetic_series, axis=0).tolist(),
            "launch_week": int(np.flatnonzero(panel.post)[0] + 1),
        },
        "spillover_sensitivity": sensitivity,
        "allocation": [asdict(item) for item in allocations],
        "assumptions": [
            "Donor markets approximate untreated potential outcomes after pre-period matching.",
            "No time-varying market shock affects treated markets exclusively.",
            "Spillover sensitivity bounds donor contamination between 0% and 35%.",
            "Budget response follows a concave saturation curve over the planning horizon.",
        ],
    }
