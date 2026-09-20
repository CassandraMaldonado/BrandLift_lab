# BrandLift Lab

**Interference-aware measurement and budget decisions for brand advertising.**

BrandLift Lab is meant to be used for measuring whether a brand campaign caused incremental outcomes, not just whether exposed users converted. It simulates a multi market ad launch, constructs a synthetic counterfactual for each treated market, diagnoses creative fatigue and spillovers and recommends a risk aware budget allocation under diminishing returns.


## The question.

> A brand campaign launched in six markets. Did it generate incremental brand actions, where did creative fatigue appear and how should the next $1M be allocated?

A naive exposed vs unexposed comparison is biased by targeting and market differences. 
User-level A/B tests can also be contaminated when content crosses network and geographic boundaries. 
BrandLift Lab treats the market as the experimental unit and makes the assumptions inspectable.

## What makes this project different?

- Builds a realistic counterfactual for each treated market using a weighted combination of comparable markets.
- Uses placebo tests to assess whether the measured lift is meaningful or could reasonably occur by chance.
- Checks how well the model fits before the campaign, so results are not trusted when the comparison is weak.
- Tests whether spillover into control markets would materially change the conclusion.
- Identifies when repeated exposure starts producing diminishing returns.
- Recommends a budget allocation while accounting for market coverage, capacity constraints, uncertainty, and diminishing returns.
- Combines statistical evidence with practical campaign considerations to produce a clear recommendation.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
brandlift-lab
```

Open [http://localhost:8000](http://localhost:8000) or print with:

```bash
python -m brandlift_lab.cli --seed 17 --budget 1000000
```

## Architecture

```mermaid
flowchart LR
    A["Market-level campaign data"] --> Q["Check data quality and pre-campaign trends"]
    Q --> S["Build a counterfactual for each treated market"]
    S --> P["Run placebo tests and check for spillover"]
    P --> F["Measure creative fatigue over time"]
    F --> O["Recommend how to allocate the next budget"]
    O --> D["Present the results in a decision brief and API"]
```

## Repository map

src/
  simulation.py         creates the market-level campaign data
  synthetic_control.py  builds counterfactuals and runs placebo tests
  diagnostics.py        checks for creative fatigue and spillover
  optimizer.py          recommends how to allocate the next budget
  analysis.py           brings the results together into a recommendation
  api.py                makes the analysis available to the web app
web/                     interactive campaign results dashboard
tests/                   tests the calculations and API behavior
docs/                    explains the methods, assumptions, and interview story

## Responsible measurement

All data is synthetic. Market-level aggregation avoids personal data, but aggregation alone is not a privacy guarantee. The system reports model fit, placebo evidence, and sensitivity ranges rather than presenting a single causal number as unquestionable truth.
